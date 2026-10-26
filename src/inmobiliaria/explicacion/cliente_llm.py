"""Interfaz desacoplada y cliente real Gemini (importación diferida)."""
from __future__ import annotations
import os
from typing import Protocol


class ClienteLLM(Protocol):
    def generar(self, prompt: str, timeout_s: float) -> str: ...


# La API de Gemini rechaza (400 INVALID_ARGUMENT) los pedidos con un plazo HTTP menor a 10 s.
# Son dos cosas distintas: LLM_TIMEOUT_S es cuánto espera la APP antes de usar la plantilla
# (lo controla ServicioExplicacionIA); el plazo HTTP es lo que se le declara a la API.
PLAZO_MINIMO_API_S = 10.0


def plazo_http_ms(timeout_s: float) -> int:
    return int(max(timeout_s, PLAZO_MINIMO_API_S) * 1000)


class ClienteGemini:
    def __init__(self, modelo: str | None = None) -> None:
        self.modelo = modelo or os.getenv('GEMINI_MODEL','')

    def generar(self, prompt: str, timeout_s: float) -> str:
        key = os.getenv('GEMINI_API_KEY','')
        if not key or not self.modelo:
            raise RuntimeError('Configurá GEMINI_API_KEY y GEMINI_MODEL antes de llamar a Gemini')
        # SDK oficial google-genai: Client(api_key), models.generate_content, response.text.
        from google import genai
        from google.genai import types
        with genai.Client(api_key=key, http_options=types.HttpOptions(timeout=plazo_http_ms(timeout_s))) as cliente:
            respuesta = cliente.models.generate_content(model=self.modelo, contents=prompt)
        return respuesta.text or ''
