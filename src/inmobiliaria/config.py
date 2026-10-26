"""Configuración por variables de entorno, sin secretos en el repositorio."""
from __future__ import annotations
import os


def _int_env(nombre: str, default: int) -> int:
    try:
        return max(1, int(os.getenv(nombre, str(default))))
    except ValueError:
        return default


def _float_env(nombre: str, default: float) -> float:
    try:
        return max(0.01, float(os.getenv(nombre, str(default))))
    except ValueError:
        return default


def db_path() -> str:
    return os.getenv('DB_PATH', 'data/inmobiliaria.db')


def min_avisos() -> int:
    return _int_env('MIN_AVISOS_ALQUILER', 5)


def top_n() -> int:
    return _int_env('TOP_N', 10)


def concurrencia_llm() -> int:
    """Explicaciones que se piden al LLM en simultáneo (bajar a 1-2 si el plan gratuito devuelve 429)."""
    return _int_env('LLM_CONCURRENCIA', 4)


def timeout_s() -> float:
    return _float_env('LLM_TIMEOUT_S', 8.0)


# --- Fuente del catálogo y proveedor de IA: dos decisiones independientes ---
# Antes DEMO=1 cambiaba las dos a la vez (catálogo sintético + IA simulada), y no había forma de
# publicar la app con el catálogo de prueba y Gemini real. DEMO se mantiene como atajo compatible.

FUENTES_CATALOGO = ('demo', 'properati')
PROVEEDORES_LLM = ('gemini', 'simulado')


def _modo_demo() -> bool:
    return os.getenv('DEMO', '0').strip() == '1'


def fuente_catalogo() -> str:
    """'demo' = data/muestra_demo.csv (sintético) · 'properati' = base cargada con scripts/cargar_catalogo.py."""
    valor = os.getenv('CATALOGO', '').strip().lower()
    if valor in FUENTES_CATALOGO:
        return valor
    return 'demo' if _modo_demo() else 'properati'


def proveedor_llm() -> str:
    """'gemini' = API real (requiere GEMINI_API_KEY y GEMINI_MODEL) · 'simulado' = ClienteDemo sin red."""
    valor = os.getenv('LLM', '').strip().lower()
    if valor in PROVEEDORES_LLM:
        return valor
    return 'simulado' if _modo_demo() else 'gemini'


def simular_falla_llm() -> bool:
    """Solo con LLM simulado: DEMO_LLM=falla fuerza el plan de respaldo (HU-07)."""
    return os.getenv('DEMO_LLM', 'ok').strip().lower() == 'falla'


def ruta_base_datos() -> str:
    """La base del catálogo de prueba se guarda aparte para no mezclarla con Properati."""
    return 'data/demo.db' if fuente_catalogo() == 'demo' else db_path()
