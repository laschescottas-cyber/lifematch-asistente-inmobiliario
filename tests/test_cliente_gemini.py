"""ClienteGemini sin red: se reemplaza genai.Client por un falso que registra lo que recibe."""
import pytest
from inmobiliaria.explicacion import cliente_llm
from inmobiliaria.explicacion.cliente_llm import ClienteGemini, plazo_http_ms
from inmobiliaria.explicacion.servicio import describir_error

genai = pytest.importorskip('google.genai')


class _Respuesta:
    text = 'ok'


class _ClienteFalso:
    recibido = {}

    def __init__(self, **kwargs):
        _ClienteFalso.recibido = kwargs
        self.models = self

    def generate_content(self, model, contents):
        _ClienteFalso.recibido['model'] = model
        return _Respuesta()

    def __enter__(self): return self
    def __exit__(self, *a): return False


@pytest.fixture
def gemini_falso(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', 'clave-de-prueba')
    monkeypatch.setattr(genai, 'Client', _ClienteFalso)
    return _ClienteFalso


@pytest.mark.parametrize('timeout_s, esperado_ms', [(8, 10000), (0.05, 10000), (10, 10000), (12, 12000)])
def test_plazo_http_nunca_menor_al_minimo_de_la_api(timeout_s, esperado_ms):
    """Bug real en la app publicada: 400 'Minimum allowed deadline is 10s' con LLM_TIMEOUT_S=8."""
    assert plazo_http_ms(timeout_s) == esperado_ms


def test_cliente_envia_plazo_valido_y_modelo(gemini_falso):
    assert ClienteGemini('gemini-de-prueba').generar('hola', 8.0) == 'ok'
    assert gemini_falso.recibido['http_options'].timeout == 10000
    assert gemini_falso.recibido['model'] == 'gemini-de-prueba'


class _Err(Exception):
    def __init__(self, code, status, message):
        super().__init__(message); self.code, self.status, self.message = code, status, message


def test_pista_400_por_plazo_no_culpa_a_la_clave():
    texto = describir_error(_Err(400, 'INVALID_ARGUMENT', 'Manually set deadline 8s is too short. Minimum allowed deadline is 10s.'))
    assert 'GEMINI_API_KEY' not in texto and 'plazo' in texto
