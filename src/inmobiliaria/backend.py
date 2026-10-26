"""Caso de uso: filtrar, puntuar, explicar, guardar y mostrar."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from inmobiliaria.modelos import Preferencia, PerfilInversor, ResultadoBusqueda, ItemResultado
from inmobiliaria.catalogo import Catalogo
from inmobiliaria.matching import MotorMatching
from inmobiliaria.explicacion.servicio import ServicioExplicacionIA
from inmobiliaria.repositorio import RepositorioSQLite
from inmobiliaria.config import concurrencia_llm


class Backend:
    def __init__(self, catalogo: Catalogo, motor: MotorMatching, servicio: ServicioExplicacionIA, repositorio: RepositorioSQLite, top_n: int = 10, concurrencia: int | None = None) -> None:
        self.catalogo,self.motor,self.servicio,self.repositorio,self.top_n = catalogo,motor,servicio,repositorio,top_n
        self.concurrencia = concurrencia if concurrencia is not None else concurrencia_llm()

    def buscar(self, pref: Preferencia, perfil: PerfilInversor | None = None) -> ResultadoBusqueda:
        if pref.validar() or (perfil and perfil.validar()):
            raise ValueError('Revisá los datos de la búsqueda')
        resultado = self.catalogo.buscar(pref)
        if not resultado.propiedades:
            return ResultadoBusqueda([],resultado.mensaje)
        propiedades = {p.id:p for p in resultado.propiedades}
        matches = self.motor.rankear(pref,resultado.propiedades,perfil)[:self.top_n]
        # 1) Se persisten los matches (SQLite, hilo principal) para que cada explicación tenga su id_match.
        for match in matches:
            self.repositorio.guardar_match(match)
        # 2) Las llamadas al LLM se hacen en paralelo: en serie, 10 explicaciones con Gemini real
        #    podían sumar decenas de segundos. El servicio nunca lanza excepciones (HU-07).
        def explicar(match):
            return self.servicio.generar_explicacion(match,propiedades[match.id_propiedad],pref,perfil)
        with ThreadPoolExecutor(max_workers=max(1,min(self.concurrencia,len(matches)))) as pool:
            explicaciones = list(pool.map(explicar,matches))
        # 3) Las explicaciones se guardan en el hilo principal (la conexión SQLite no se comparte entre hilos).
        items: list[ItemResultado] = []
        for match, explicacion in zip(matches,explicaciones):
            self.repositorio.guardar_explicacion(explicacion)
            items.append(ItemResultado(propiedades[match.id_propiedad],match,explicacion))
        return ResultadoBusqueda(items,None)
