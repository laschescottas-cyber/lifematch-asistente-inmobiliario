"""Catálogo académico reproducible y proveedor LLM falso para demo sin red."""
from __future__ import annotations
import csv
from pathlib import Path
from inmobiliaria.catalogo import COLUMNAS, Catalogo
from inmobiliaria.repositorio import RepositorioSQLite


class ClienteDemo:
    def __init__(self, falla: bool = False) -> None:
        self.falla = falla

    def generar(self, prompt: str, timeout_s: float) -> str:
        if self.falla:
            raise RuntimeError('Fallo simulado para HU-07')
        return ('Esta propiedad muestra ventajas para tus prioridades según los datos del aviso. '
                'El porcentaje surge de LifeMatch; las preferencias y los avisos determinan el resultado. '
                'No se certifican distancias que no figuren en el catálogo. '
                'Si hay rentabilidad, es una estimación basada en avisos de alquiler, no una garantía.')


def crear_csv_demo(ruta: str) -> None:
    """No representa el mercado actual: avisos completamente inventados para tests/demos."""
    archivo = Path(ruta)
    archivo.parent.mkdir(parents=True,exist_ok=True)
    if archivo.exists(): return
    ventas = [
      ('v1','Almagro','Departamento',190000,3,70,'Colegio cerca, parque y subte; home office y contrafrente, ascensor.'),
      ('v2','Almagro','Departamento',160000,2,60,'Subte y metrobús; edificio con oficinas.'),
      ('v3','Almagro','Departamento',210000,3,72,'Parque, colegio, plaza y tranquilidad, patio.'),
      ('v4','Almagro','Departamento',155000,2,56,'Ascensor y rampa, clínica cercana, estación de subte.'),
      ('v5','Almagro','Departamento',230000,4,90,'Jardín, colegios, silencio y home office.'),
      ('v6','Caballito','Casa',180000,3,110,'Patio, plaza, colegio y tren.'),
      ('v7','Almagro','Departamento',140000,2,60,'Tren y subte; departamento tranquilo.'),
      ('v8','Almagro','Departamento',250000,4,100,'Parque, escuela, escritorio y subte.'),
    ]
    alquileres = [('a'+str(i),'Almagro','Departamento',precio,2,60,'Alquiler mensual') for i,precio in enumerate((400,420,440,460,480,500),1)]
    with archivo.open('w',encoding='utf-8',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=COLUMNAS)
        writer.writeheader()
        for ident,zona,tipo,precio,amb,sup,texto in ventas+alquileres:
            operacion = 'Alquiler' if ident.startswith('a') else 'Venta'
            row = dict.fromkeys(COLUMNAS,'')
            row.update(id=ident,ad_type='Propiedad',start_date='2020-01-01',end_date='9999-12-31',created_on='2020-01-01',lat='-34.6',lon='-58.4',l1='Argentina',l2='Capital Federal',l3=zona,rooms=amb,surface_covered=sup,currency='USD',price_period='Mensual' if operacion=='Alquiler' else '',title=f'{tipo} en {zona}',description=texto,property_type=tipo,operation_type=operacion,price=precio)
            writer.writerow(row)


def cargar_demo_si_vacio(repo: RepositorioSQLite, ruta: str = 'data/muestra_demo.csv') -> None:
    crear_csv_demo(ruta)
    if repo.con.execute('SELECT COUNT(*) FROM propiedad').fetchone()[0]==0:
        Catalogo(repo).cargar_csv(ruta)
