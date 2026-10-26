"""Orquestación XAI con timeout efectivo y plan B silencioso."""
from __future__ import annotations
from datetime import datetime
import json
import logging
import queue
import re
import threading
import os
from inmobiliaria.modelos import Match,Propiedad,Preferencia,PerfilInversor,Explicacion
from inmobiliaria.explicacion.cliente_llm import ClienteLLM
from inmobiliaria.explicacion.plantilla import PlantillaRespaldo
from inmobiliaria.config import timeout_s as config_timeout

logger = logging.getLogger(__name__)
_PATRON_CLAVE = re.compile(r'AIza[0-9A-Za-z_\-]{8,}')
_PISTAS = {
    400: 'revisá GEMINI_API_KEY (clave inválida o mal copiada) o el formato del pedido',
    401: 'revisá GEMINI_API_KEY',
    403: 'la clave no tiene permiso para este modelo o proyecto',
    404: 'revisá GEMINI_MODEL: el modelo no existe o no está habilitado para la cuenta',
    429: 'se superó el límite del plan; bajá TOP_N o LLM_CONCURRENCIA, o probá más tarde',
}


def describir_error(exc: Exception) -> str:
    """Resumen del error del proveedor para el registro: tipo, código, motivo y una pista.

    Nunca incluye la clave: cualquier texto con forma de clave de Google se enmascara.
    """
    partes = [type(exc).__name__]
    codigo = getattr(exc, 'code', None)
    if codigo is not None:
        partes.append(str(codigo))
    estado = getattr(exc, 'status', None)
    if estado:
        partes.append(str(estado))
    mensaje = getattr(exc, 'message', None) or str(exc)
    if mensaje:
        partes.append('· ' + _PATRON_CLAVE.sub('AIza***', str(mensaje))[:300])
    pista = _PISTAS.get(codigo) if isinstance(codigo, int) else None
    if pista:
        partes.append('→ ' + pista)
    return ' '.join(partes)
INSTRUCCIONES = '''Sos un asesor inmobiliario. Redactá en español rioplatense una explicación de 60 a 80 palabras
de por qué esta propiedad fue recomendada.
Reglas:
- Usá SOLO los datos provistos. No inventes nada.
- Mencioná primero las variables de "a_favor" (las que más aportaron) y después las limitaciones.
- Si "en_contra" o "sin_dato" no están vacíos, mencioná una limitación (si una variable de entorno vale 0, decí que "el aviso no lo menciona").
- Si hay "rentabilidad", mencioná el porcentaje y el alquiler en que se basa, y aclará que es una estimación y no una garantía.
- No uses listas ni encabezados. Respondé solo con el texto.'''


class ServicioExplicacionIA:
    modelo_llm: str

    def __init__(self, cliente: ClienteLLM, plantilla: PlantillaRespaldo, timeout_s: float | None = None) -> None:
        self.cliente = cliente
        self.plantilla = plantilla
        self.timeout_s = timeout_s if timeout_s is not None else config_timeout()
        self.modelo_llm = os.getenv('GEMINI_MODEL','')

    def invocar_api(self, prompt: str) -> str | None:
        """No espera el final de hilos colgados (daemon); registra errores sin datos privados."""
        resultados: queue.Queue[tuple[str | None,Exception | None]] = queue.Queue(maxsize=1)
        def trabajo() -> None:
            try:
                resultados.put_nowait((self.cliente.generar(prompt,self.timeout_s),None))
            except Exception as exc:
                resultados.put_nowait((None,exc))
        hilo = threading.Thread(target=trabajo,daemon=True)
        hilo.start()
        try:
            texto, error = resultados.get(timeout=max(.001,self.timeout_s))
            if error:
                logger.warning('El servicio de IA no respondió correctamente: %s',describir_error(error))
                return None
            return texto.strip() if texto and texto.strip() else None
        except queue.Empty:
            logger.warning('El servicio de IA excedió el timeout')
            return None

    def usar_plantilla_respaldo(self, match: Match, prop: Propiedad, objetivo: str = 'vivir', perfil: PerfilInversor | None = None) -> str:
        return self.plantilla.redactar(match,prop,objetivo,perfil)

    def generar_explicacion(self, match: Match, prop: Propiedad, pref: Preferencia | None = None, perfil: PerfilInversor | None = None) -> Explicacion:
        objetivo = pref.objetivo if pref else ('invertir' if perfil else 'vivir')
        try:
            # No se usa Usuario: jamás se incorpora nombre o email en el prompt.
            payload = match.generar_explicacion_request(prop,objetivo,perfil)
            prompt = INSTRUCCIONES+'\n\nDatos (JSON):\n'+json.dumps(payload,ensure_ascii=False)
            texto = self.invocar_api(prompt)
            if texto is not None:
                if objetivo=='invertir' and not any(w in texto.lower() for w in ('estimación','estimada','estimado')):
                    texto += ' La rentabilidad es una estimación a partir de avisos de alquiler del dataset, no una garantía.'
                return Explicacion(None,match.id_match,texto,'llm',datetime.now())
        except Exception:
            logger.exception('Fallo al preparar la explicación; se utilizará la plantilla')
        try:
            texto = self.usar_plantilla_respaldo(match,prop,objetivo,perfil)
        except Exception:
            logger.exception('Fallo al armar la plantilla')
            texto = f'Esta propiedad tiene una compatibilidad del {round(match.porcentaje_compatibilidad)}% con tu perfil.'
            if objetivo=='invertir': texto += ' Rentabilidad: sin datos suficientes de alquiler en la zona.'
        return Explicacion(None,match.id_match,texto,'plantilla',datetime.now())
