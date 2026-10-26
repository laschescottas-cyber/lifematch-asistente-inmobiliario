from dataclasses import replace
from inmobiliaria.filtros import FiltrosDuros
from inmobiliaria.modelos import MENSAJE_SIN_RESULTADOS


def test_excluye_otra_operacion(propiedad,pref_vivir):
    assert not replace(propiedad,operation_type='Alquiler').cumple_filtros_duros(pref_vivir)


def test_excluye_fuera_de_presupuesto_y_otra_moneda(propiedad,pref_vivir):
    assert not replace(propiedad,precio=300000).cumple_filtros_duros(pref_vivir)
    assert not replace(propiedad,moneda='ARS').cumple_filtros_duros(pref_vivir)


def test_excluye_fuera_de_zona(propiedad,pref_vivir):
    assert not replace(propiedad,ubicacion='Buenos Aires, Palermo').cumple_filtros_duros(pref_vivir)


def test_excluye_menos_ambientes(propiedad,pref_vivir):
    assert not replace(propiedad,ambientes=1).cumple_filtros_duros(pref_vivir)


def test_sin_resultados_devuelve_mensaje(propiedad,pref_vivir):
    pref_vivir.zona='Rosario'
    res=FiltrosDuros().aplicar([propiedad],pref_vivir)
    assert res.propiedades==[] and res.mensaje==MENSAJE_SIN_RESULTADOS
