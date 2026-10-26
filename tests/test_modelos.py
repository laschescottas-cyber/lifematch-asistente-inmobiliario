import pytest
from inmobiliaria.modelos import Usuario, Preferencia, PerfilInversor, Propiedad, normalizar_texto, objetivo_de


def test_texto_y_arquetipo():
    assert normalizar_texto('  ÁLMaGRo  ') == 'almagro'
    assert objetivo_de('Inversor') == 'invertir'
    with pytest.raises(ValueError): objetivo_de('No existe')


def test_preferencias_y_validaciones():
    u = Usuario(None, 'Visitante', 'Inversor')
    pref = u.completar_preferencias('Alquiler', 100, 'USD', 'Almagro', 2, {'rentabilidad': .8, 'conectividad': .2})
    assert pref.operacion == 'Venta'
    assert pref.normalizar() == {'rentabilidad': .8, 'conectividad': .2}
    assert pref.validar() == []
    assert PerfilInversor(None, None, 4, 5).validar() == []
    assert PerfilInversor(None, None, 0, 0, -1).validar() == ['rentabilidad_objetivo','horizonte_anios','tipo_cambio']
    with pytest.raises(ValueError): pref.actualizar_peso('rentabilidad', 3)


def test_propiedad_filtros():
    pref = Preferencia(None, None, 'vivir', 'Venta', 250000, 'USD', 'Almagro', 2, {'colegio': 1})
    prop = Propiedad(id='a', operation_type='Venta', precio=200000, moneda='USD', ubicacion='Capital Federal, Almagro', ambientes=2)
    assert prop.cumple_filtros_duros(pref)
    assert not Propiedad(id='b',operation_type='Alquiler',precio=1000,moneda='USD',ubicacion='Almagro',ambientes=3).cumple_filtros_duros(pref)
