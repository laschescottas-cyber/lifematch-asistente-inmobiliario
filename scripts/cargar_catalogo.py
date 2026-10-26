"""Uso: python scripts/cargar_catalogo.py data/properati.csv"""
from __future__ import annotations
import argparse
import logging
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from inmobiliaria.catalogo import Catalogo
from inmobiliaria.repositorio import RepositorioSQLite
from inmobiliaria.config import db_path


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('ruta_csv',help='Ruta al CSV Properati')
    args = parser.parse_args()
    repo = RepositorioSQLite(db_path())
    try:
        print(Catalogo(repo).cargar_csv(args.ruta_csv))
    finally:
        repo.cerrar()


if __name__ == '__main__':
    main()
