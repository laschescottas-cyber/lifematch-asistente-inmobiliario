"""Interfaz desacoplada y cliente real Gemini (importación diferida)."""
from __future__ import annotations
import os
from typing import Protocol


class ClienteLLM(Protocol):
    def generar(self, prompt: str, timeout_s: float) -> str: ...


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
        with genai.Client(api_key=key, http_options=types.HttpOptions(timeout=int(timeout_s*1000))) as cliente:
            respuesta = cliente.models.generate_content(model=self.modelo, contents=prompt)
        return respuesta.text or ''
