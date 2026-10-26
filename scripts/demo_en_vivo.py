"""Demostración sin clave ni internet; usa datos sintéticos, NO el dataset real."""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from inmobiliaria.ui.demo import crear_csv_demo,ClienteDemo
from inmobiliaria.repositorio import RepositorioSQLite
from inmobiliaria.catalogo import Catalogo
from inmobiliaria.modelos import Usuario,PerfilInversor
from inmobiliaria.matching import MotorMatching
from inmobiliaria.rentabilidad import EstimadorRentabilidad
from inmobiliaria.explicacion.servicio import ServicioExplicacionIA
from inmobiliaria.explicacion.plantilla import PlantillaRespaldo
from inmobiliaria.backend import Backend


def ejecutar(repo: RepositorioSQLite, nombre: str, pesos: dict[str,float], invertir: bool = False, falla: bool = False, zona: str = 'Almagro') -> None:
    usuario=Usuario(None,'Visitante',nombre)
    repo.guardar_usuario(usuario)
    pref=usuario.completar_preferencias('Venta',260000,'USD',zona,2,pesos)
    perfil=PerfilInversor(None,None,4.0,5) if invertir else None
    repo.guardar_preferencia(pref,perfil)
    cat=Catalogo(repo)
    backend=Backend(cat,MotorMatching(EstimadorRentabilidad(repo),cat),ServicioExplicacionIA(ClienteDemo(falla),PlantillaRespaldo(),.1),repo,3)
    res=backend.buscar(pref,perfil)
    print(f'\n=== {nombre} / Zona: {zona} / Falla simulada: {falla} ===')
    print(res.mensaje or f'{len(res.items)} resultados')
    for i in res.items:
        r=i.match.rentabilidad
        renta = ' | rentabilidad sin dato' if r and not r.disponible else f' | rentabilidad {r.rentabilidad_bruta_anual:.2f}%' if r else ''
        print(f'- {i.propiedad.id}: {i.propiedad.title} | match {i.match.porcentaje_compatibilidad}%{renta} | explicación: {i.explicacion.origen}')
        print('  '+i.explicacion.texto)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix='inmobiliaria-demo-') as d:
        csv_path=str(Path(d)/'muestra_demo.csv')
        crear_csv_demo(csv_path)
        repo=RepositorioSQLite(str(Path(d)/'demo.db'))
        try:
            carga=Catalogo(repo).cargar_csv(csv_path)
            print(f'Catálogo sintético cargado: {carga}')
            ejecutar(repo,'Familia con hijos',{'colegio':1,'espacios_verdes':.8,'conectividad':.6,'espacio_trabajo':.8,'silencio':.4,'accesibilidad_salud':.2})
            ejecutar(repo,'Inversor',{'rentabilidad':.8,'precio_m2':.6,'conectividad':.2},invertir=True)
            ejecutar(repo,'Inversor',{'rentabilidad':.8,'precio_m2':.6,'conectividad':.2},invertir=True,zona='Caballito') # sin comparables
            ejecutar(repo,'Profesional remoto',{'espacio_trabajo':1,'silencio':1,'conectividad':.8})
            ejecutar(repo,'Familia con hijos',{'colegio':1},falla=True)
            ejecutar(repo,'Familia con hijos',{'colegio':1},zona='Zona sin avisos')
        finally:repo.cerrar()


if __name__=='__main__':main()
