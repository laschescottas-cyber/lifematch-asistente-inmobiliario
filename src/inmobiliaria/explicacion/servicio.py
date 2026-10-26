"""Orquestación XAI con timeout efectivo y plan B silencioso."""
from __future__ import annotations
from datetime import datetime
import json
import logging
import queue
import threading
import os
from inmobiliaria.modelos import Match,Propiedad,Preferencia,PerfilInversor,Explicacion
from inmobiliaria.explicacion.cliente_llm import ClienteLLM
from inmobiliaria.explicacion.plantilla import PlantillaRespaldo
from inmobiliaria.config import timeout_s as config_timeout

logger = logging.getLogger(__name__)
INSTRUCCIONES = '''Sos un asesor inmobiliario. Redactá en español rioplatense una explicación de 60 a 80 palabras
de por qué esta propiedad fue recomendada.
Reglas:
- Usá SOLO los datos provistos. No inventes nada.
- Mencioná las variables de "a_favor".
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
                logger.warning('El servicio de IA no respondió correctamente (%s)',type(error).__name__)
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
