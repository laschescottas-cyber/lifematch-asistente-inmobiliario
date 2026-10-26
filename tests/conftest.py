"""Fixtures sintéticas: nunca acceden a Kaggle ni a Gemini."""
from __future__ import annotations
import csv
import pytest
from inmobiliaria.repositorio import RepositorioSQLite
from inmobiliaria.modelos import Propiedad, Preferencia, Usuario
from inmobiliaria.catalogo import COLUMNAS


@pytest.fixture
def repo(tmp_path):
    bd = RepositorioSQLite(str(tmp_path/'bd.db'))
    yield bd
    bd.cerrar()


@pytest.fixture
def pref_vivir():
    return Preferencia(None,None,'vivir','Venta',260000,'USD','Almagro',2,{'colegio':1.,'espacios_verdes':.8,'conectividad':.6,'espacio_trabajo':.8,'silencio':.4,'accesibilidad_salud':.2})


@pytest.fixture
def propiedad():
    return Propiedad(id='venta1',id_propiedad='venta1',l2='Capital Federal',l3='Almagro',operation_type='Venta',property_type='Departamento',rooms=3,ambientes=3,price=200000,precio=200000,currency='USD',moneda='USD',ubicacion='Capital Federal, Almagro',surface_covered=70,precio_m2=200000/70,title='Departamento con parque',caracteristicas={'colegio':1,'espacios_verdes':1,'conectividad':1,'espacio_trabajo':0,'silencio':0,'accesibilidad_salud':0})


@pytest.fixture
def csv_sintetico(tmp_path):
    ruta=tmp_path/'prueba.csv'
    def fila(ident: str,op: str,precio: int,sup: str='60', moneda: str='USD', texto: str='parque y subte'):
        d=dict.fromkeys(COLUMNAS,'')
        d.update(id=ident,ad_type='Aviso',start_date='2020-01-01',end_date='9999-12-31',created_on='2020-01-01',lat='-34.6',lon='-58.4',l1='Argentina',l2='Capital Federal',l3='Almagro',rooms='2.0',surface_total='70',surface_covered=sup,currency=moneda,price_period='Mensual',title='departamento',description=texto,property_type='Departamento',operation_type=op,price=str(precio))
        return d
    filas=[fila('v1','Venta',150000),fila('v2','Venta',180000,''),fila('invalid','Venta',0),fila('a1','Alquiler',400),fila('a2','Alquiler',500),fila('a3','Alquiler',600),fila('a4','Alquiler',550),fila('a5','Alquiler',650),fila('v3','Venta',200000,texto='parque tranquilo')]
    filas[0]['lat'],filas[0]['lon']='-58.4','-34.6'
    with ruta.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNAS);writer.writeheader();writer.writerows(filas)
    return ruta
