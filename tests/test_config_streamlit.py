"""La app publicada no muestra detalles técnicos de errores a los visitantes."""
from pathlib import Path
import tomllib

RAIZ = Path(__file__).resolve().parents[1]


def test_visitante_no_ve_tracebacks():
    config = tomllib.loads((RAIZ / '.streamlit' / 'config.toml').read_text(encoding='utf-8'))
    assert config['client']['showErrorDetails'] == 'none'


def test_secretos_locales_ignorados_por_git():
    assert '.streamlit/secrets.toml' in (RAIZ / '.gitignore').read_text(encoding='utf-8').splitlines()
