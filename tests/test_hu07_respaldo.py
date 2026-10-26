import time
from inmobiliaria.matching import MotorMatching
from inmobiliaria.explicacion.servicio import ServicioExplicacionIA
from inmobiliaria.explicacion.plantilla import PlantillaRespaldo
from inmobiliaria.modelos import Preferencia,PerfilInversor,Rentabilidad


class ClienteFalla:
    def generar(self,prompt,timeout_s):raise RuntimeError('Falla simulada')
class ClienteVacio:
    def generar(self,prompt,timeout_s):return '   '
class ClienteLento:
    def generar(self,prompt,timeout_s):time.sleep(.3);return 'llegó muy tarde'


def test_timeout_usa_plantilla(propiedad,pref_vivir):
    m=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    t=time.monotonic()
    e=ServicioExplicacionIA(ClienteLento(),PlantillaRespaldo(),timeout_s=.03).generar_explicacion(m,propiedad,pref_vivir)
    assert e.origen=='plantilla' and time.monotonic()-t<.15


def test_error_del_cliente_usa_plantilla(propiedad,pref_vivir):
    m=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    assert ServicioExplicacionIA(ClienteFalla(),PlantillaRespaldo(),.05).generar_explicacion(m,propiedad,pref_vivir).origen=='plantilla'


def test_respuesta_vacia_usa_plantilla(propiedad,pref_vivir):
    m=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    assert ServicioExplicacionIA(ClienteVacio(),PlantillaRespaldo(),.05).generar_explicacion(m,propiedad,pref_vivir).origen=='plantilla'


def test_nunca_lanza_excepcion(propiedad,pref_vivir):
    m=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    e=ServicioExplicacionIA(ClienteFalla(),PlantillaRespaldo(),.05).generar_explicacion(m,propiedad,pref_vivir)
    assert isinstance(e.texto,str) and e.texto


def test_plantilla_textos_exactos(propiedad,pref_vivir):
    m=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    texto=PlantillaRespaldo().redactar(m,propiedad)
    assert texto.startswith(f'Esta propiedad tiene una compatibilidad del {round(m.porcentaje_compatibilidad)}% con tu perfil.')
    assert 'Lo que más suma:' in texto and 'Lo que menos se cumple:' in texto


def test_plantilla_inversor(propiedad):
    pref=Preferencia(None,None,'invertir','Venta',300000,'USD','Almagro',2,{'rentabilidad':1,'precio_m2':.5})
    perfil=PerfilInversor(None,None,4,5)
    renta=Rentabilidad(10,700,4.2,5,'USD',True)
    m=MotorMatching().calcular_compatibilidad(pref,propiedad,perfil,renta)
    texto=PlantillaRespaldo().redactar(m,propiedad,'invertir',perfil)
    assert 'Rentabilidad bruta anual estimada:' in texto and 'Es una estimación, no una garantía.' in texto


class _ErrorGemini(Exception):
    """Imita google.genai.errors.ClientError (code, status, message)."""
    def __init__(self, code, status, message):
        super().__init__(message); self.code, self.status, self.message = code, status, message


def test_registro_indica_codigo_motivo_y_pista(propiedad, pref_vivir, caplog):
    class ClienteModeloInexistente:
        def generar(self, prompt, timeout_s):
            raise _ErrorGemini(404, 'NOT_FOUND', 'models/gemini-x is not found for API version v1beta')
    m = MotorMatching().calcular_compatibilidad(pref_vivir, propiedad)
    with caplog.at_level('WARNING'):
        e = ServicioExplicacionIA(ClienteModeloInexistente(), PlantillaRespaldo(), .5).generar_explicacion(m, propiedad, pref_vivir)
    assert e.origen == 'plantilla'
    assert '404 NOT_FOUND' in caplog.text and 'GEMINI_MODEL' in caplog.text


def test_registro_nunca_muestra_la_clave():
    from inmobiliaria.explicacion.servicio import describir_error
    texto = describir_error(_ErrorGemini(400, 'INVALID_ARGUMENT', 'API key not valid: AIzaSyD-ejemplo_1234567890abcdef'))
    assert 'AIzaSyD' not in texto and 'AIza***' in texto and 'GEMINI_API_KEY' in texto
