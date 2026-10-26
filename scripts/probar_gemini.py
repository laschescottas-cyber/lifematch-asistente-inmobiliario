"""Prueba MANUAL de la API real. No se ejecuta desde pytest."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from inmobiliaria.explicacion.cliente_llm import ClienteGemini
from inmobiliaria.config import timeout_s

if __name__ == '__main__':
    print(ClienteGemini().generar('Respondé únicamente: API disponible.',timeout_s()))
