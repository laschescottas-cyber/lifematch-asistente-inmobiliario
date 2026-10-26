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
