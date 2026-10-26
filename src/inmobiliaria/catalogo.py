"""Carga de CSV de Properati con streaming, limpieza y reglas documentadas."""
from __future__ import annotations
import csv
import io
import logging
import re
from pathlib import Path
from statistics import median
from inmobiliaria.modelos import Propiedad, Preferencia, ResultadoFiltro, ResumenCarga, normalizar_texto
from inmobiliaria.repositorio import RepositorioSQLite
from inmobiliaria.filtros import FiltrosDuros
from inmobiliaria.config import min_avisos

logger = logging.getLogger(__name__)
COLUMNAS = ['id','ad_type','start_date','end_date','created_on','lat','lon','l1','l2','l3','l4','l5','l6','rooms','bedrooms','bathrooms','surface_total','surface_covered','currency','price_period','title','description','property_type','operation_type','price']
PALABRAS_CLAVE: dict[str,list[str]] = {
 'colegio':['colegio*','escuela*','jardin de infantes','nivel inicial','primaria','secundaria','universidad*'],
 'espacios_verdes':['parque*','plaza*','espacio verde','espacios verdes','jardin','patio','bosque*','reserva ecologica'],
 'conectividad':['subte','metrobus','tren','colectivo*','estacion*','premetro','medios de transporte','transporte publico'],
 'espacio_trabajo':['home office','oficina*','escritorio','espacio de trabajo','apto profesional','coworking'],
 'silencio':['tranquil*','silenc*','contrafrente','pasaje'],
 'accesibilidad_salud':['ascensor*','rampa*','discapacitad*','accesible','hospital*','clinica*','sanatorio*','centro de salud'],
}


def _reparar(texto: str) -> str:
    if any(s in texto for s in ('Ã','â€')):
        try:
            return texto.encode('latin-1').decode('utf-8')
        except UnicodeError:
            return texto
    return texto


def _num(dato: str | float | None) -> float | None:
    try:
        valor = float(dato) if dato is not None and str(dato).strip() else None
        return valor if valor is not None and __import__('math').isfinite(valor) else None
    except (TypeError, ValueError):
        return None


def _caracteristicas(texto: str) -> dict[str,float]:
    t = normalizar_texto(texto)
    salida: dict[str,float] = {}
    for variable, palabras in PALABRAS_CLAVE.items():
        cumple = False
        for termino in palabras:
            prefijo = termino.endswith('*')
            base = termino[:-1] if prefijo else termino
            regex = r'(?<!\w)' + re.escape(base) + (r'\w*' if prefijo else '') + r'(?!\w)'
            if re.search(regex,t):
                cumple = True
                break
        salida[variable] = float(cumple)
    return salida


class Catalogo:
    def __init__(self, repositorio: RepositorioSQLite) -> None:
        self.repositorio = repositorio
        self._ultimo_completado = False

    def normalizar_datos(self, fila: dict) -> Propiedad | None:
        fila = {k: _reparar(str(v or '').strip()) for k, v in fila.items()}
        precio = _num(fila.get('price'))
        ambientes = _num(fila.get('rooms'))
        if not fila.get('id') or not precio or precio<=0 or not fila.get('currency') or not fila.get('operation_type') or not fila.get('l3') or ambientes is None or ambientes < 1:
            return None
        if normalizar_texto(fila['operation_type']) not in ('venta','alquiler'):
            return None
        numericas = ('lat','lon','rooms','bedrooms','bathrooms','surface_total','surface_covered','price')
        args: dict = {k: (_num(fila.get(k)) if k in numericas else fila.get(k) or None) for k in COLUMNAS}
        args['id'] = fila['id']
        args['title'] = fila.get('title','')
        args['description'] = fila.get('description','')
        swapped = False
        if args['lat'] is not None and args['lon'] is not None and not -56 <= args['lat'] <= -21 and -56 <= args['lon'] <= -21:
            args['lat'], args['lon'] = args['lon'], args['lat']
            swapped = True
        if normalizar_texto(args['operation_type']) == 'venta':
            args['price_period'] = None
        prop = Propiedad(**args)
        prop.id_propiedad = prop.id
        prop.precio = float(precio)
        prop.moneda = str(args['currency'])
        prop.ubicacion = ', '.join(str(args[k]) for k in ('l2','l3','l4','l5','l6') if args[k])
        prop.ambientes = int(ambientes)
        sup = prop.surface_covered if (prop.surface_covered or 0)>0 else prop.surface_total
        prop.precio_m2 = precio/sup if sup and sup>0 else None
        prop.caracteristicas = _caracteristicas(prop.title+' '+prop.description)
        self._ultimo_completado = swapped or prop.precio_m2 is None
        return prop

    def cargar_csv(self, ruta: str, lote: int = 5000) -> ResumenCarga:
        if lote < 1: raise ValueError('El lote debe ser mayor que cero')
        resumen = ResumenCarga(0,0,0,0)
        cache: list[Propiedad] = []
        with open(ruta, newline='', encoding='utf-8-sig') as fh:
            lector = csv.reader(fh)
            cabecera = next(lector,None)
            if cabecera is None: return resumen
            if len(cabecera)==1:
                cabecera = next(csv.reader([cabecera[0]]),[])
            cabecera = [s.strip() for s in cabecera]
            if cabecera != COLUMNAS:
                raise ValueError('Cabecera CSV incompatible: se requieren las 25 columnas originales de Properati')
            for raw in lector:
                resumen.leidos += 1
                try:
                    if len(raw)==1 and ',' in raw[0]:
                        raw = next(csv.reader(io.StringIO(raw[0],newline='')), [])
                    if len(raw)!=25:
                        resumen.descartados += 1
                        continue
                    prop = self.normalizar_datos(dict(zip(COLUMNAS,raw)))
                    if prop is None:
                        resumen.descartados += 1
                        continue
                    resumen.validos += 1
                    resumen.completados += int(self._ultimo_completado)
                    cache.append(prop)
                    if len(cache) >= lote:
                        self.repositorio.guardar_propiedades(cache)
                        cache.clear()
                    if resumen.leidos % 10000 == 0:
                        logger.info('CSV: %s avisos leídos', resumen.leidos)
                except (ValueError, TypeError, csv.Error):
                    resumen.descartados += 1
            if cache:
                self.repositorio.guardar_propiedades(cache)
        logger.info('Carga finalizada: %s', resumen)
        return resumen

    def buscar(self, pref: Preferencia) -> ResultadoFiltro:
        return FiltrosDuros().aplicar(self.repositorio.consultar_propiedades(pref),pref)

    def mediana_precio_m2(self, zona: str, tipo: str, moneda: str) -> float | None:
        valores = self.repositorio.valores_precio_m2(zona,tipo,'Venta',moneda)
        return float(median(valores)) if len(valores) >= min_avisos() else None
