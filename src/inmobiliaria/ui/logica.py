"""Transformaciones de UI, testeables sin Streamlit."""
from __future__ import annotations
from inmobiliaria.modelos import ItemResultado, Preferencia, PerfilInversor, ETIQUETAS


def slider_a_peso(valor: int) -> float:
    if not isinstance(valor,int) or not 0 <= valor <= 5:
        raise ValueError('El control debe estar entre 0 y 5')
    return valor/5


def pesos_desde_sliders(valores: dict[str,int]) -> dict[str,float]:
    return {clave:slider_a_peso(valor) for clave,valor in valores.items()}


def validar_formulario(pref: Preferencia, perfil: PerfilInversor | None = None) -> list[str]:
    return pref.validar()+([] if perfil is None else perfil.validar())


def ordenar_items(items: list[ItemResultado], criterio: str) -> list[ItemResultado]:
    if criterio not in ('mayor compatibilidad','menor compatibilidad'):
        raise ValueError('Orden no reconocido')
    descendente = criterio == 'mayor compatibilidad'
    return sorted(items,key=lambda item: ((-1 if descendente else 1)*item.match.porcentaje_compatibilidad,item.propiedad.id))


def formatear_precio(precio: float, moneda: str) -> str:
    return f'{moneda} {precio:,.0f}'.replace(',','.')


def formatear_porcentaje(valor: float) -> str:
    return f'{valor:.1f} %'.replace('.',',')


def icono_para(property_type: str | None) -> str:
    tipo = (property_type or '').casefold()
    if any(s in tipo for s in ('casa','house')): return '🏠'
    if any(s in tipo for s in ('departamento','apartment','ph')): return '🏢'
    return '🏘️'


def formatear_superficie(m2: float | None) -> str:
    return f'{m2:g} m²'.replace('.',',') if m2 else 'superficie sin dato'


def texto_origen(origen: str, demo: bool = False) -> str:
    """Rótulo honesto del origen de la explicación (HU-06/HU-07, sin mostrar errores técnicos)."""
    if origen == 'llm':
        return 'Modo demo: explicación simulada, no generada por Gemini.' if demo else 'Explicación generada con inteligencia artificial (Gemini).'
    return 'Explicación automática armada con los datos del cálculo.'
