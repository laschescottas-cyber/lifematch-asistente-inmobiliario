"""Medianas de avisos comparables y rentabilidad bruta, sin ML."""
from __future__ import annotations
from statistics import median
from inmobiliaria.modelos import Propiedad, Rentabilidad, PerfilInversor
from inmobiliaria.repositorio import RepositorioSQLite
from inmobiliaria.config import min_avisos as config_min_avisos


class EstimadorRentabilidad:
    def __init__(self, repositorio: RepositorioSQLite, min_avisos: int | None = None) -> None:
        self.repositorio = repositorio
        self.min_avisos = min_avisos if min_avisos is not None else config_min_avisos()
        if self.min_avisos < 1: raise ValueError('min_avisos debe ser mayor que cero')

    def mediana_alquiler_m2(self, zona: str, tipo: str, moneda: str, tipo_cambio: float | None = None) -> tuple[float | None,int]:
        precios: list[float] = []
        for row in self.repositorio.alquileres_comparables(zona,tipo):
            sup = row['surface_covered'] if (row['surface_covered'] or 0)>0 else row['surface_total']
            if not sup or sup <= 0: continue
            monto = float(row['price'])
            desde = str(row['currency']).upper()
            hacia = moneda.upper()
            if desde != hacia:
                if not tipo_cambio or tipo_cambio <= 0: continue
                if desde=='ARS' and hacia=='USD': monto /= tipo_cambio
                elif desde=='USD' and hacia=='ARS': monto *= tipo_cambio
                else: continue
            precios.append(monto/sup)
        if len(precios) < self.min_avisos:
            return None, len(precios)
        return float(median(precios)), len(precios)

    def estimar(self, prop: Propiedad, perfil: PerfilInversor | None = None) -> Rentabilidad:
        tipo_cambio = perfil.tipo_cambio if perfil else None
        mediana_m2, cantidad = self.mediana_alquiler_m2(prop.l3 or '', prop.property_type or '', prop.moneda, tipo_cambio)
        sup = prop.surface_covered if (prop.surface_covered or 0)>0 else prop.surface_total
        if mediana_m2 is None or sup is None or sup <= 0 or prop.precio <= 0:
            return Rentabilidad(mediana_m2,None,None,cantidad,prop.moneda,False)
        alquiler = mediana_m2*sup
        return Rentabilidad(mediana_m2,alquiler,(alquiler*12/prop.precio)*100,cantidad,prop.moneda,True)
