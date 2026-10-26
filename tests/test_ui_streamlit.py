"""Recorrido real de la app con streamlit.testing (sin navegador, sin red, modo DEMO).

Cubre los criterios de interfaz de HU-01, HU-02, HU-03 y HU-08 que la lógica pura no alcanza.
"""
from __future__ import annotations
from pathlib import Path
import pytest

pytest.importorskip('streamlit')
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / 'app.py')


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # data/demo.db y data/muestra_demo.csv quedan en una carpeta temporal
    monkeypatch.setenv('DEMO', '1')
    monkeypatch.setenv('DEMO_LLM', 'ok')
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    return at


def _boton(at, etiqueta):
    return next(b for b in at.button if b.label == etiqueta)


def _recorrer(at, perfil, zona='Almagro'):
    at.radio[0].set_value(perfil)
    _boton(at, 'Continuar').click().run()
    at.text_input[0].set_value(zona)
    _boton(at, 'Continuar a las prioridades').click().run()
    _boton(at, 'Revisar búsqueda').click().run()
    _boton(at, 'Buscar propiedades').click().run()
    assert not at.exception, at.exception
    return at


def test_hu01_muestra_los_cinco_perfiles(app):
    assert app.radio[0].options == ['Familia con hijos', 'Profesional remoto', 'Pareja joven', 'Adulto mayor', 'Inversor']


def test_hu08_ruta_vivir_muestra_tarjetas_ordenadas(app):
    at = _recorrer(app, 'Familia con hijos')
    assert at.success and 'Encontré' in at.success[0].value
    valores = [float(m.value.replace(' %', '').replace(',', '.')) for m in at.metric]
    assert valores and valores == sorted(valores, reverse=True)


def test_hu08_ruta_invertir_muestra_rentabilidad_separada(app):
    at = _recorrer(app, 'Inversor')
    textos = ' '.join(m.value for m in at.markdown)
    assert 'Rentabilidad bruta anual estimada' in textos
    assert at.metric  # el LifeMatch se muestra aparte de la rentabilidad


def test_hu03_sin_resultados_sugiere_ajustar(app):
    at = _recorrer(app, 'Familia con hijos', zona='Zona inexistente')
    assert at.warning and 'ampliar' in at.warning[0].value


def test_hu02_zona_vacia_avisa_dato_faltante(app):
    _boton(app, 'Continuar').click().run()
    app.text_input[0].set_value('   ')
    _boton(app, 'Continuar a las prioridades').click().run()
    assert app.error and 'zona' in app.error[0].value
