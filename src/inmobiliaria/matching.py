"""Cálculo determinístico LifeMatch: suma ponderada, no modelo entrenado."""
from __future__ import annotations
from datetime import date
from inmobiliaria.modelos import Preferencia, Propiedad, Match, DetalleVariable, Rentabilidad, PerfilInversor, VARIABLES, variables_del_objetivo
from inmobiliaria.rentabilidad import EstimadorRentabilidad
from inmobiliaria.catalogo import Catalogo


class MotorMatching:
    pesos: dict[str,float]

    def __init__(self, estimador: EstimadorRentabilidad | None = None, catalogo: Catalogo | None = None) -> None:
        self.estimador = estimador
        self.catalogo = catalogo
        self.pesos = {}

    def asignar_pesos(self, pref: Preferencia) -> None:
        self.pesos = pref.normalizar()

    def calcular_compatibilidad(self, pref: Preferencia, prop: Propiedad, perfil: PerfilInversor | None = None, rentabilidad: Rentabilidad | None = None, mediana_precio_m2: float | None = None) -> Match:
        pesos = {v: pref.pesos.get(v, 0) for v in variables_del_objetivo(pref.objetivo) if pref.pesos.get(v,0)>0}
        cumplimientos: dict[str,float] = {}
        sin_dato: list[str] = []
        for v in pesos:
            if v == 'rentabilidad':
                if rentabilidad is None or not rentabilidad.disponible or perfil is None or perfil.rentabilidad_objetivo <= 0 or rentabilidad.rentabilidad_bruta_anual is None:
                    sin_dato.append(v)
                    continue
                c = rentabilidad.rentabilidad_bruta_anual / perfil.rentabilidad_objetivo
            elif v == 'precio_m2':
                if not prop.precio_m2 or not mediana_precio_m2 or mediana_precio_m2 <= 0:
                    sin_dato.append(v)
                    continue
                c = mediana_precio_m2 / prop.precio_m2
            else:
                c = prop.caracteristicas.get(v,0.0)
            cumplimientos[v] = max(0.,min(1.,c))
        total = sum(pesos[v] for v in cumplimientos)
        detalle = {v: DetalleVariable(pesos[v],c,round(100*pesos[v]/total*c,1)) for v,c in cumplimientos.items()} if total else {}
        compatibilidad = round(100*sum(pesos[v]*c for v,c in cumplimientos.items())/total,1) if total else 0.
        return Match(None,pref.id_preferencia,prop.id_propiedad or prop.id,compatibilidad,date.today(),detalle,rentabilidad,[v for v in VARIABLES if v in sin_dato])

    def rankear(self, pref: Preferencia, propiedades: list[Propiedad], perfil: PerfilInversor | None = None) -> list[Match]:
        self.asignar_pesos(pref)
        mediana_cache: dict[tuple[str,str,str],float | None] = {}
        salida: list[Match] = []
        for prop in propiedades:
            renta: Rentabilidad | None = None
            mediana_m2: float | None = None
            if pref.objetivo == 'invertir':
                renta = self.estimador.estimar(prop,perfil) if self.estimador else Rentabilidad(None,None,None,0,prop.moneda,False)
                clave = (prop.l3 or '',prop.property_type or '',prop.moneda)
                if clave not in mediana_cache:
                    mediana_cache[clave] = self.catalogo.mediana_precio_m2(*clave) if self.catalogo else None
                mediana_m2 = mediana_cache[clave]
            salida.append(self.calcular_compatibilidad(pref,prop,perfil,renta,mediana_m2))
        return sorted(salida,key=lambda m:(-m.porcentaje_compatibilidad,m.id_propiedad))
