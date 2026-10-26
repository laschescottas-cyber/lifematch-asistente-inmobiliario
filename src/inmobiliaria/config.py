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
