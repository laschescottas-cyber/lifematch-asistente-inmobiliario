"""Persistencia SQLite y reconstrucción de entidades del dominio."""
from __future__ import annotations
import sqlite3
from dataclasses import fields
from pathlib import Path
from inmobiliaria.modelos import (Usuario, Preferencia, PerfilInversor, Propiedad, Match, Explicacion, Rentabilidad, normalizar_texto)

SCHEMA = '''
CREATE TABLE IF NOT EXISTS usuario (id_usuario INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, email TEXT NOT NULL DEFAULT '', arquetipo TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS preferencia (id_preferencia INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER NOT NULL REFERENCES usuario(id_usuario), objetivo TEXT NOT NULL CHECK (objetivo IN ('vivir', 'invertir')), operacion TEXT NOT NULL, presupuesto REAL NOT NULL, moneda TEXT NOT NULL, zona TEXT NOT NULL, ambientes INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS peso_preferencia (id_preferencia INTEGER NOT NULL REFERENCES preferencia(id_preferencia), variable TEXT NOT NULL, peso REAL NOT NULL, PRIMARY KEY (id_preferencia, variable));
CREATE TABLE IF NOT EXISTS perfil_inversor (id_perfil INTEGER PRIMARY KEY AUTOINCREMENT, id_preferencia INTEGER NOT NULL UNIQUE REFERENCES preferencia(id_preferencia), rentabilidad_objetivo REAL NOT NULL, horizonte_anios INTEGER NOT NULL, tipo_cambio REAL);
CREATE TABLE IF NOT EXISTS propiedad (id TEXT PRIMARY KEY, ad_type TEXT, start_date TEXT, end_date TEXT, created_on TEXT, lat REAL, lon REAL, l1 TEXT, l2 TEXT, l3 TEXT, l4 TEXT, l5 TEXT, l6 TEXT, rooms REAL, bedrooms REAL, bathrooms REAL, surface_total REAL, surface_covered REAL, currency TEXT, price_period TEXT, title TEXT NOT NULL DEFAULT '', description TEXT NOT NULL DEFAULT '', property_type TEXT, operation_type TEXT, price REAL, precio_m2 REAL);
CREATE INDEX IF NOT EXISTS ix_propiedad_busqueda ON propiedad (operation_type, currency, price, rooms);
CREATE INDEX IF NOT EXISTS ix_propiedad_zona ON propiedad (l3, property_type, operation_type);
CREATE TABLE IF NOT EXISTS caracteristica (id_propiedad TEXT NOT NULL REFERENCES propiedad(id), variable TEXT NOT NULL, valor REAL NOT NULL, PRIMARY KEY (id_propiedad, variable));
CREATE TABLE IF NOT EXISTS "match" (id_match INTEGER PRIMARY KEY AUTOINCREMENT, id_preferencia INTEGER NOT NULL REFERENCES preferencia(id_preferencia), id_propiedad TEXT NOT NULL REFERENCES propiedad(id), porcentaje_compatibilidad REAL NOT NULL, fecha TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS rentabilidad (id_rentabilidad INTEGER PRIMARY KEY AUTOINCREMENT, id_match INTEGER NOT NULL UNIQUE REFERENCES "match"(id_match), mediana_alquiler_m2 REAL, alquiler_mensual_est REAL, rentabilidad_bruta_anual REAL, avisos_usados INTEGER NOT NULL, moneda TEXT NOT NULL, disponible INTEGER NOT NULL CHECK (disponible IN (0, 1)));
CREATE TABLE IF NOT EXISTS explicacion (id_explicacion INTEGER PRIMARY KEY AUTOINCREMENT, id_match INTEGER NOT NULL UNIQUE REFERENCES "match"(id_match), texto TEXT NOT NULL, origen TEXT NOT NULL CHECK (origen IN ('llm', 'plantilla')), fecha_generacion TEXT NOT NULL);
'''
COLUMNAS = ['id','ad_type','start_date','end_date','created_on','lat','lon','l1','l2','l3','l4','l5','l6','rooms','bedrooms','bathrooms','surface_total','surface_covered','currency','price_period','title','description','property_type','operation_type','price','precio_m2']


class RepositorioSQLite:
    def __init__(self, ruta_db: str) -> None:
        if ruta_db != ':memory:':
            Path(ruta_db).parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(ruta_db, timeout=30)
        self.con.row_factory = sqlite3.Row
        self.con.execute('PRAGMA foreign_keys = ON')
        self.con.create_function('normalizar_texto',1,normalizar_texto,deterministic=True)
        self.crear_esquema()

    def crear_esquema(self) -> None:
        self.con.executescript(SCHEMA)

    def guardar_usuario(self, usuario: Usuario) -> int:
        with self.con:
            cur = self.con.execute('INSERT INTO usuario (nombre,email,arquetipo) VALUES (?,?,?)', (usuario.nombre, usuario.email, usuario.arquetipo))
        usuario.id_usuario = int(cur.lastrowid)
        return usuario.id_usuario

    def guardar_preferencia(self, pref: Preferencia, perfil: PerfilInversor | None = None) -> int:
        errores = pref.validar()
        if errores or (perfil and perfil.validar()):
            raise ValueError(f'Preferencias inválidas: {errores or perfil.validar()}')
        if pref.id_usuario is None:
            raise ValueError('Guardá primero el usuario')
        with self.con:
            cur = self.con.execute('INSERT INTO preferencia (id_usuario,objetivo,operacion,presupuesto,moneda,zona,ambientes) VALUES (?,?,?,?,?,?,?)', (pref.id_usuario,pref.objetivo,pref.operacion,pref.presupuesto,pref.moneda,pref.zona,pref.ambientes))
            pref.id_preferencia = int(cur.lastrowid)
            self.con.executemany('INSERT INTO peso_preferencia (id_preferencia,variable,peso) VALUES (?,?,?)', [(pref.id_preferencia,v,p) for v,p in pref.pesos.items()])
            if perfil:
                c = self.con.execute('INSERT INTO perfil_inversor (id_preferencia,rentabilidad_objetivo,horizonte_anios,tipo_cambio) VALUES (?,?,?,?)', (pref.id_preferencia,perfil.rentabilidad_objetivo,perfil.horizonte_anios,perfil.tipo_cambio))
                perfil.id_perfil = int(c.lastrowid)
                perfil.id_preferencia = pref.id_preferencia
        return pref.id_preferencia

    def guardar_propiedades(self, propiedades: list[Propiedad]) -> int:
        """Guarda un lote sin alterar referencias de matches históricos al actualizar avisos."""
        if not propiedades:
            return 0
        asignaciones = ', '.join(f'{c}=excluded.{c}' for c in COLUMNAS if c != 'id')
        sql = f'INSERT INTO propiedad ({",".join(COLUMNAS)}) VALUES ({",".join("?" for _ in COLUMNAS)}) ON CONFLICT(id) DO UPDATE SET {asignaciones}'
        with self.con:
            self.con.executemany(sql, [[getattr(p, c) for c in COLUMNAS] for p in propiedades])
            for p in propiedades:
                self.con.execute('DELETE FROM caracteristica WHERE id_propiedad=?', (p.id,))
            self.con.executemany('INSERT INTO caracteristica (id_propiedad,variable,valor) VALUES (?,?,?)', [(p.id, v, valor) for p in propiedades for v, valor in p.caracteristicas.items()])
        return len(propiedades)

    @staticmethod
    def _desde_fila(fila: sqlite3.Row, caracteristicas: dict[str, float]) -> Propiedad:
        claves = set(fila.keys())
        original = {f.name: fila[f.name] for f in fields(Propiedad) if f.name in claves and f.name not in {'precio_m2'}}
        prop = Propiedad(**original)
        prop.id_propiedad = prop.id
        prop.precio = float(prop.price or 0)
        prop.moneda = prop.currency or ''
        prop.ubicacion = ', '.join(p for p in (prop.l2,prop.l3,prop.l4,prop.l5,prop.l6) if p)
        prop.ambientes = int(prop.rooms or 0)
        prop.precio_m2 = fila['precio_m2']
        prop.caracteristicas = caracteristicas
        return prop

    def consultar_propiedades(self, pref: Preferencia) -> list[Propiedad]:
        """Reduce el universo en SQL antes de construir las entidades."""
        # Filtrado de zona en dos pasos: SQLite usa LIKE por espacio; Python resuelve acentos.
        # Para búsquedas que atraviesan l2-l6, aplicar el filtro final en FiltrosDuros.
        sql = """SELECT * FROM propiedad WHERE lower(operation_type)=lower(?) AND lower(currency)=lower(?) AND price<=? AND rooms>=?
                 AND instr(normalizar_texto(coalesce(l2,'')||' '||coalesce(l3,'')||' '||coalesce(l4,'')||' '||coalesce(l5,'')||' '||coalesce(l6,'')),normalizar_texto(?))>0"""
        params = [pref.operacion,pref.moneda,pref.presupuesto,pref.ambientes,pref.zona]
        rows = self.con.execute(sql,params).fetchall()
        ids = [r['id'] for r in rows]
        chars: dict[str,dict[str,float]] = {i:{} for i in ids}
        for start in range(0,len(ids),900):
            chunk = ids[start:start+900]
            if not chunk: continue
            for row in self.con.execute(f'SELECT * FROM caracteristica WHERE id_propiedad IN ({",".join("?" for _ in chunk)})',chunk):
                chars[row['id_propiedad']][row['variable']] = row['valor']
        return [self._desde_fila(r, chars[r['id']]) for r in rows]

    def valores_precio_m2(self, l3: str, property_type: str, operation_type: str, moneda: str) -> list[float]:
        q = '''SELECT precio_m2 FROM propiedad WHERE lower(coalesce(l3,''))=lower(?) AND lower(coalesce(property_type,''))=lower(?) AND lower(operation_type)=lower(?) AND lower(currency)=lower(?) AND precio_m2>0'''
        return [r[0] for r in self.con.execute(q,(l3,property_type,operation_type,moneda))]

    def alquileres_comparables(self, l3: str, tipo: str) -> list[sqlite3.Row]:
        return self.con.execute('''SELECT price,currency,surface_covered,surface_total,price_period FROM propiedad WHERE lower(coalesce(l3,''))=lower(?) AND lower(coalesce(property_type,''))=lower(?) AND lower(operation_type)='alquiler' AND lower(coalesce(price_period,''))='mensual' AND price>0''',(l3,tipo)).fetchall()

    def guardar_match(self, match: Match) -> int:
        if match.id_preferencia is None:
            raise ValueError('No se puede persistir el match sin preferencia')
        with self.con:
            cur = self.con.execute('INSERT INTO "match" (id_preferencia,id_propiedad,porcentaje_compatibilidad,fecha) VALUES (?,?,?,?)', (match.id_preferencia,match.id_propiedad,match.porcentaje_compatibilidad,match.fecha.isoformat()))
            match.id_match = int(cur.lastrowid)
            r = match.rentabilidad
            if r is not None:
                self.con.execute('INSERT INTO rentabilidad (id_match,mediana_alquiler_m2,alquiler_mensual_est,rentabilidad_bruta_anual,avisos_usados,moneda,disponible) VALUES (?,?,?,?,?,?,?)', (match.id_match,r.mediana_alquiler_m2,r.alquiler_mensual_est,r.rentabilidad_bruta_anual,r.avisos_usados,r.moneda,int(r.disponible)))
        return match.id_match

    def guardar_explicacion(self, explicacion: Explicacion) -> int:
        with self.con:
            cur = self.con.execute('INSERT INTO explicacion (id_match,texto,origen,fecha_generacion) VALUES (?,?,?,?)', (explicacion.id_match,explicacion.texto,explicacion.origen,explicacion.fecha_generacion.isoformat()))
        explicacion.id_explicacion = int(cur.lastrowid)
        return explicacion.id_explicacion

    def cerrar(self) -> None:
        self.con.close()
