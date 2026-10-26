"""Lanzar con: streamlit run app.py"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent/'src'))
from inmobiliaria.ui.pantallas import mostrar

if __name__ == '__main__':
    mostrar()
