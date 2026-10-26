import json
from inmobiliaria.modelos import Preferencia,PerfilInversor,Rentabilidad
from inmobiliaria.matching import MotorMatching
from inmobiliaria.explicacion.servicio import ServicioExplicacionIA,INSTRUCCIONES
from inmobiliaria.explicacion.plantilla import PlantillaRespaldo


class ClienteCaptura:
    def __init__(self, texto='Es una estimación explicada a partir de la información.'):self.prompt='';self.texto=texto
    def generar(self,prompt,timeout_s):self.prompt=prompt;return self.texto


def test_prompt_contiene_instrucciones_y_json(propiedad,pref_vivir):
    fake=ClienteCaptura()
    match=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    ServicioExplicacionIA(fake,PlantillaRespaldo()).generar_explicacion(match,propiedad,pref_vivir)
    assert 'Sos un asesor inmobiliario' in fake.prompt
    assert '"porcentaje"' in fake.prompt
    assert '"a_favor"' in fake.prompt


def test_prompt_no_contiene_nombre_ni_email(propiedad,pref_vivir):
    fake=ClienteCaptura()
    # PII de Usuario no llega al servicio de XAI.
    propiedad.title='Departamento'
    match=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    ServicioExplicacionIA(fake,PlantillaRespaldo()).generar_explicacion(match,propiedad,pref_vivir)
    assert 'Natalia' not in fake.prompt and 'personal@ejemplo.test' not in fake.prompt
    assert 'email' not in fake.prompt.lower()


def test_explicacion_llm_origen_llm(propiedad,pref_vivir):
    match=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    e=ServicioExplicacionIA(ClienteCaptura('Recomendada por tus prioridades.'),PlantillaRespaldo()).generar_explicacion(match,propiedad,pref_vivir)
    assert e.origen=='llm' and 'prioridades' in e.texto


def test_inversor_incluye_aclaracion_de_estimacion(propiedad):
    pref=Preferencia(None,None,'invertir','Venta',300000,'USD','Almagro',2,{'rentabilidad':1})
    perfil=PerfilInversor(None,None,4,5)
    renta=Rentabilidad(10,700,4.2,5,'USD',True)
    match=MotorMatching().calcular_compatibilidad(pref,propiedad,perfil,renta)
    e=ServicioExplicacionIA(ClienteCaptura('Buena propiedad.'),PlantillaRespaldo()).generar_explicacion(match,propiedad,pref,perfil)
    assert 'estimación' in e.texto.lower() and 'garantía' in e.texto.lower()


def test_respuesta_rapida_se_usa(propiedad,pref_vivir):
    match=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    assert ServicioExplicacionIA(ClienteCaptura('respuesta sin latencia'),PlantillaRespaldo(),.1).generar_explicacion(match,propiedad,pref_vivir).texto=='respuesta sin latencia'
