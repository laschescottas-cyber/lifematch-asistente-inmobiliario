import pytest
from inmobiliaria.modelos import ARQUETIPOS,Usuario
from inmobiliaria.arquetipos import PESOS_POR_DEFECTO,DESCRIPCIONES


def test_muestra_5_perfiles():
    assert len(ARQUETIPOS)==5 and len(DESCRIPCIONES)==5


def test_seleccionar_arquetipo_precarga_pesos_por_defecto():
    u=Usuario(None,'Visitante','Familia con hijos')
    for a in ARQUETIPOS:
        u.seleccionar_arquetipo(a)
        assert PESOS_POR_DEFECTO[a]


def test_inversor_fija_objetivo_invertir_y_operacion_venta():
    u=Usuario(None,'Visitante','Inversor')
    assert (p:=u.completar_preferencias('Alquiler',230000,'USD','Almagro',2,{'rentabilidad':.8})).operacion=='Venta'
    assert p.objetivo=='invertir'


def test_arquetipo_invalido_lanza_error():
    with pytest.raises(ValueError): Usuario(None,'Visitante','Familia con hijos').seleccionar_arquetipo('inventado')
