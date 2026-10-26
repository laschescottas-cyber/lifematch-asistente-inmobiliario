from inmobiliaria.modelos import Usuario,PerfilInversor,Preferencia
from inmobiliaria.ui.logica import validar_formulario,slider_a_peso,pesos_desde_sliders


def test_respuestas_se_guardan_como_variables_normalizadas():
    pref=Usuario(None,'Visitante','Pareja joven').completar_preferencias('Alquiler',1000,'USD','Almagro',2,{'conectividad':1,'espacios_verdes':1})
    assert pref.objetivo=='vivir' and pref.normalizar()=={'espacios_verdes':.5,'conectividad':.5}


def test_falta_dato_indispensable_indica_cual(pref_vivir):
    pref_vivir.zona=''
    assert validar_formulario(pref_vivir)==['zona']


def test_ruta_inversor_registra_capital_rentabilidad_horizonte_tipo_cambio():
    pref=Usuario(None,'Visitante','Inversor').completar_preferencias('Venta',250000,'USD','Almagro',2,{'rentabilidad':.8})
    perfil=PerfilInversor(None,None,4.0,10,1100.)
    assert not validar_formulario(pref,perfil)
    assert (pref.presupuesto,perfil.rentabilidad_objetivo,perfil.horizonte_anios,perfil.tipo_cambio)==(250000,4,10,1100)


def test_slider_a_peso():
    assert slider_a_peso(4)==.8 and pesos_desde_sliders({'colegio':5})=={'colegio':1.}


def test_normalizar_suma_uno(pref_vivir):
    assert abs(sum(pref_vivir.normalizar().values())-1)<1e-12
