"""Filtros obligatorios anteriores a LifeMatch."""
from __future__ import annotations
from inmobiliaria.modelos import Propiedad, Preferencia, ResultadoFiltro, MENSAJE_SIN_RESULTADOS


class FiltrosDuros:
    def aplicar(self, propiedades: list[Propiedad], pref: Preferencia) -> ResultadoFiltro:
        filtradas = [prop for prop in propiedades if prop.cumple_filtros_duros(pref)]
        return ResultadoFiltro(filtradas, None if filtradas else MENSAJE_SIN_RESULTADOS)
