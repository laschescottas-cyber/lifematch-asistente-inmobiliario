"""Explicaciones determinísticas para contingencias del proveedor LLM."""
from __future__ import annotations
from inmobiliaria.modelos import Match, Propiedad, PerfilInversor, ETIQUETAS


def _unir(items: list[str]) -> str:
    if len(items)<2: return ''.join(items)
    return ', '.join(items[:-1])+' y '+items[-1]


class PlantillaRespaldo:
    def redactar(self, match: Match, prop: Propiedad, objetivo: str = 'vivir', perfil: PerfilInversor | None = None) -> str:
        oraciones = [f'Esta propiedad tiene una compatibilidad del {round(match.porcentaje_compatibilidad)}% con tu perfil.']
        claves = [ETIQUETAS[v] for v in match.variables_clave(3)]
        debiles = [ETIQUETAS[v] for v in match.variables_debiles(2)]
        if claves: oraciones.append('Lo que más suma: '+_unir(claves)+'.')
        if debiles: oraciones.append('Lo que menos se cumple: '+_unir(debiles)+'.')
        no_mencionadas = [ETIQUETAS[v] for v,d in match.detalle.items() if d.cumplimiento == 0 and v not in ('rentabilidad','precio_m2')]
        if no_mencionadas: oraciones.append('El aviso no lo menciona para: '+_unir(no_mencionadas)+'.')
        if match.variables_sin_dato: oraciones.append('Sin datos suficientes para: '+_unir([ETIQUETAS[v] for v in match.variables_sin_dato])+'.')
        if objetivo == 'invertir':
            r = match.rentabilidad
            if r and r.disponible:
                meta = perfil.rentabilidad_objetivo if perfil else 0
                oraciones.append(f'Rentabilidad bruta anual estimada: {r.rentabilidad_bruta_anual:.1f}% (objetivo {meta:g}%), con un alquiler estimado de {r.alquiler_mensual_est:.2f} {r.moneda} por mes según {r.avisos_usados} avisos de alquiler. Es una estimación, no una garantía.')
            else:
                oraciones.append('Rentabilidad: sin datos suficientes de alquiler en la zona.')
        return ' '.join(oraciones)
