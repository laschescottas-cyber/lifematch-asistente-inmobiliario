"""Caso de uso: filtrar, puntuar, explicar, guardar y mostrar."""
from __future__ import annotations
from inmobiliaria.modelos import Preferencia, PerfilInversor, ResultadoBusqueda, ItemResultado
from inmobiliaria.catalogo import Catalogo
from inmobiliaria.matching import MotorMatching
from inmobiliaria.explicacion.servicio import ServicioExplicacionIA
from inmobiliaria.repositorio import RepositorioSQLite


class Backend:
    def __init__(self, catalogo: Catalogo, motor: MotorMatching, servicio: ServicioExplicacionIA, repositorio: RepositorioSQLite, top_n: int = 10) -> None:
        self.catalogo,self.motor,self.servicio,self.repositorio,self.top_n = catalogo,motor,servicio,repositorio,top_n

    def buscar(self, pref: Preferencia, perfil: PerfilInversor | None = None) -> ResultadoBusqueda:
        if pref.validar() or (perfil and perfil.validar()):
            raise ValueError('Revisá los datos de la búsqueda')
        resultado = self.catalogo.buscar(pref)
        if not resultado.propiedades:
            return ResultadoBusqueda([],resultado.mensaje)
        propiedades = {p.id:p for p in resultado.propiedades}
        items: list[ItemResultado] = []
        for match in self.motor.rankear(pref,resultado.propiedades,perfil)[:self.top_n]:
            prop = propiedades[match.id_propiedad]
            self.repositorio.guardar_match(match)
            explicacion = self.servicio.generar_explicacion(match,prop,pref,perfil)
            self.repositorio.guardar_explicacion(explicacion)
            items.append(ItemResultado(prop,match,explicacion))
        return ResultadoBusqueda(items,None)
