"""Entidades del proyecto, respetando el documento del TP."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
import unicodedata
import re

ARQUETIPOS: list[str] = ['Familia con hijos', 'Profesional remoto', 'Pareja joven', 'Adulto mayor', 'Inversor']
OBJETIVOS: list[str] = ['vivir', 'invertir']
OPERACIONES: list[str] = ['Venta', 'Alquiler']
VARIABLES_VIVIR: list[str] = ['colegio', 'espacios_verdes', 'conectividad', 'espacio_trabajo', 'silencio', 'accesibilidad_salud']
VARIABLES_INVERSOR: list[str] = ['rentabilidad', 'precio_m2', 'conectividad']
VARIABLES: list[str] = ['colegio', 'espacios_verdes', 'conectividad', 'espacio_trabajo', 'silencio', 'accesibilidad_salud', 'rentabilidad', 'precio_m2']
ETIQUETAS: dict[str, str] = {'colegio': 'cercanía a colegios', 'espacios_verdes':'espacios verdes', 'conectividad':'conectividad', 'espacio_trabajo':'espacio de trabajo', 'silencio':'silencio', 'accesibilidad_salud':'accesibilidad y centros de salud', 'rentabilidad':'rentabilidad estimada', 'precio_m2':'precio por m²'}
MENSAJE_SIN_RESULTADOS = 'No hay propiedades que cumplan tus condiciones obligatorias. Probá ampliar el presupuesto, la zona o bajar los ambientes.'


def normalizar_texto(texto: str) -> str:
    """Normaliza texto para buscar palabras y barrios sin diferencias de acento."""
    sin_tildes = ''.join(c for c in unicodedata.normalize('NFKD', texto.lower()) if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', sin_tildes).strip()


def objetivo_de(arquetipo: str) -> str:
    if arquetipo not in ARQUETIPOS:
        raise ValueError('Arquetipo desconocido')
    return 'invertir' if arquetipo == 'Inversor' else 'vivir'


def variables_del_objetivo(objetivo: str) -> list[str]:
    if objetivo not in OBJETIVOS:
        raise ValueError('Objetivo desconocido')
    return VARIABLES_INVERSOR.copy() if objetivo == 'invertir' else VARIABLES_VIVIR.copy()


@dataclass
class Usuario:
    id_usuario: int | None
    nombre: str
    arquetipo: str
    email: str = ''

    def seleccionar_arquetipo(self, arquetipo: str) -> None:
        objetivo_de(arquetipo)
        self.arquetipo = arquetipo

    def completar_preferencias(self, operacion: str, presupuesto: float, moneda: str, zona: str, ambientes: int, pesos: dict[str, float]) -> Preferencia:
        objetivo = objetivo_de(self.arquetipo)
        return Preferencia(None, self.id_usuario, objetivo, 'Venta' if objetivo == 'invertir' else operacion, presupuesto, moneda, zona, ambientes, pesos.copy())


@dataclass
class Preferencia:
    id_preferencia: int | None
    id_usuario: int | None
    objetivo: str
    operacion: str
    presupuesto: float
    moneda: str
    zona: str
    ambientes: int
    pesos: dict[str, float] = field(default_factory=dict)

    def normalizar(self) -> dict[str, float]:
        candidatos = {v: self.pesos.get(v, 0) for v in variables_del_objetivo(self.objetivo) if self.pesos.get(v, 0) > 0}
        total = sum(candidatos.values())
        return {v: p / total for v, p in candidatos.items()} if total else {}

    def actualizar_peso(self, variable: str, valor: float) -> None:
        if variable not in VARIABLES or not 0 <= valor <= 1:
            raise ValueError('Variable o peso inválidos')
        self.pesos[variable] = valor

    def validar(self) -> list[str]:
        errores = []
        if self.operacion not in OPERACIONES or (self.objetivo == 'invertir' and self.operacion != 'Venta'):
            errores.append('operacion')
        if self.presupuesto <= 0 or not self.moneda.strip():
            errores.append('presupuesto')
        if not self.zona.strip():
            errores.append('zona')
        if self.ambientes < 1:
            errores.append('ambientes')
        if not self.normalizar() or any(not 0 <= p <= 1 for p in self.pesos.values()):
            errores.append('pesos')
        return errores


@dataclass
class PerfilInversor:
    id_perfil: int | None
    id_preferencia: int | None
    rentabilidad_objetivo: float
    horizonte_anios: int
    tipo_cambio: float | None = None

    def validar(self) -> list[str]:
        res: list[str] = []
        if self.rentabilidad_objetivo <= 0:
            res.append('rentabilidad_objetivo')
        if self.horizonte_anios < 1:
            res.append('horizonte_anios')
        if self.tipo_cambio is not None and self.tipo_cambio <= 0:
            res.append('tipo_cambio')
        return res


@dataclass
class Propiedad:
    id: str
    ad_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    created_on: str | None = None
    lat: float | None = None
    lon: float | None = None
    l1: str | None = None
    l2: str | None = None
    l3: str | None = None
    l4: str | None = None
    l5: str | None = None
    l6: str | None = None
    rooms: float | None = None
    bedrooms: float | None = None
    bathrooms: float | None = None
    surface_total: float | None = None
    surface_covered: float | None = None
    currency: str | None = None
    price_period: str | None = None
    title: str = ''
    description: str = ''
    property_type: str | None = None
    operation_type: str | None = None
    price: float | None = None
    id_propiedad: str = ''
    precio: float = 0.0
    moneda: str = ''
    ubicacion: str = ''
    ambientes: int = 0
    precio_m2: float | None = None
    caracteristicas: dict[str, float] = field(default_factory=dict)

    def cumple_filtros_duros(self, pref: Preferencia) -> bool:
        return (normalizar_texto(self.operation_type or '') == normalizar_texto(pref.operacion)
                and self.precio <= pref.presupuesto and self.moneda.casefold() == pref.moneda.casefold()
                and normalizar_texto(pref.zona) in normalizar_texto(self.ubicacion)
                and self.ambientes >= pref.ambientes)


@dataclass
class DetalleVariable:
    peso: float
    cumplimiento: float
    aporte: float


@dataclass
class Rentabilidad:
    mediana_alquiler_m2: float | None
    alquiler_mensual_est: float | None
    rentabilidad_bruta_anual: float | None
    avisos_usados: int
    moneda: str
    disponible: bool


@dataclass
class Match:
    id_match: int | None
    id_preferencia: int | None
    id_propiedad: str
    porcentaje_compatibilidad: float
    fecha: date
    detalle: dict[str, DetalleVariable] = field(default_factory=dict)
    rentabilidad: Rentabilidad | None = None
    variables_sin_dato: list[str] = field(default_factory=list)

    def variables_clave(self, n: int = 3) -> list[str]:
        return sorted((v for v, d in self.detalle.items() if d.aporte > 0), key=lambda v: (-self.detalle[v].aporte, VARIABLES.index(v)))[:n]

    def variables_debiles(self, n: int = 2) -> list[str]:
        return sorted((v for v, d in self.detalle.items() if d.peso * (1 - d.cumplimiento) > 0), key=lambda v: (-self.detalle[v].peso * (1 - self.detalle[v].cumplimiento), VARIABLES.index(v)))[:n]

    def generar_explicacion_request(self, prop: Propiedad, objetivo: str = 'vivir', perfil: PerfilInversor | None = None) -> dict:
        claves = self.variables_clave(3)
        debiles = self.variables_debiles(2)
        resultado = {
            'porcentaje': round(self.porcentaje_compatibilidad), 'objetivo': objetivo,
            'propiedad': {'titulo': prop.title, 'tipo': prop.property_type, 'ubicacion': prop.ubicacion, 'precio': prop.precio, 'moneda': prop.moneda, 'ambientes': prop.ambientes, 'superficie_m2': prop.surface_covered or prop.surface_total},
            'a_favor': [{'variable': ETIQUETAS[v], 'aporte': self.detalle[v].aporte} for v in claves],
            'en_contra': [{'variable': ETIQUETAS[v], 'peso': self.detalle[v].peso, 'cumplimiento': self.detalle[v].cumplimiento} for v in debiles],
            'sin_dato': [ETIQUETAS[v] for v in self.variables_sin_dato],
        }
        if objetivo == 'invertir' and self.rentabilidad and self.rentabilidad.disponible:
            r = self.rentabilidad
            resultado['rentabilidad'] = {'bruta_anual_pct': r.rentabilidad_bruta_anual, 'objetivo_pct': perfil.rentabilidad_objetivo if perfil else None, 'alquiler_mensual_est': r.alquiler_mensual_est, 'moneda': r.moneda, 'avisos_usados': r.avisos_usados}
        return resultado


@dataclass
class Explicacion:
    id_explicacion: int | None
    id_match: int | None
    texto: str
    origen: str
    fecha_generacion: datetime


@dataclass
class ResumenCarga:
    leidos: int
    validos: int
    descartados: int
    completados: int


@dataclass
class ResultadoFiltro:
    propiedades: list[Propiedad]
    mensaje: str | None


@dataclass
class ItemResultado:
    propiedad: Propiedad
    match: Match
    explicacion: Explicacion


@dataclass
class ResultadoBusqueda:
    items: list[ItemResultado]
    mensaje: str | None
