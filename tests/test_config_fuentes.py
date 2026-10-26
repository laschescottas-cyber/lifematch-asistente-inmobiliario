"""Fuente del catálogo y proveedor de IA son configuraciones independientes."""
import pytest
from inmobiliaria import config


@pytest.fixture(autouse=True)
def entorno_limpio(monkeypatch):
    for v in ('DEMO', 'DEMO_LLM', 'CATALOGO', 'LLM', 'DB_PATH'):
        monkeypatch.delenv(v, raising=False)


def test_por_defecto_properati_y_gemini():
    assert (config.fuente_catalogo(), config.proveedor_llm()) == ('properati', 'gemini')
    assert config.ruta_base_datos() == 'data/inmobiliaria.db'


def test_demo_1_sigue_activando_ambos_modos_de_prueba(monkeypatch):
    monkeypatch.setenv('DEMO', '1')
    assert (config.fuente_catalogo(), config.proveedor_llm()) == ('demo', 'simulado')
    assert config.ruta_base_datos() == 'data/demo.db'


def test_catalogo_de_prueba_con_gemini_real(monkeypatch):
    """Caso de la app publicada: no hay base de Properati, pero la IA debe ser real (Eje 1)."""
    monkeypatch.setenv('CATALOGO', 'demo')
    assert (config.fuente_catalogo(), config.proveedor_llm()) == ('demo', 'gemini')


def test_variables_explicitas_ganan_sobre_demo(monkeypatch):
    monkeypatch.setenv('DEMO', '1')
    monkeypatch.setenv('LLM', 'Gemini')
    assert (config.fuente_catalogo(), config.proveedor_llm()) == ('demo', 'gemini')


def test_valor_invalido_usa_el_defecto(monkeypatch):
    monkeypatch.setenv('CATALOGO', 'kaggle')
    monkeypatch.setenv('LLM', 'chatgpt')
    assert (config.fuente_catalogo(), config.proveedor_llm()) == ('properati', 'gemini')


def test_falla_simulada(monkeypatch):
    assert not config.simular_falla_llm()
    monkeypatch.setenv('DEMO_LLM', 'falla')
    assert config.simular_falla_llm()
