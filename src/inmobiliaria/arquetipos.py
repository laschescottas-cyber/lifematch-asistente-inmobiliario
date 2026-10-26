"""Prioridades precargadas, editables por el usuario."""
from __future__ import annotations
from inmobiliaria.modelos import ARQUETIPOS

PESOS_POR_DEFECTO: dict[str,dict[str,float]] = {
 'Familia con hijos': {'colegio':1.0,'espacios_verdes':.8,'conectividad':.6,'espacio_trabajo':.8,'silencio':.4,'accesibilidad_salud':.2},
 # TODO(equipo): validar pesos de profesional remoto con los integrantes.
 'Profesional remoto': {'colegio':0,'espacios_verdes':.2,'conectividad':.8,'espacio_trabajo':1.0,'silencio':1.0,'accesibilidad_salud':.2},
 # TODO(equipo): validar pesos de pareja joven, especialmente "vida de barrio" (sin variable propia).
 'Pareja joven': {'colegio':.2,'espacios_verdes':.6,'conectividad':1.0,'espacio_trabajo':.2,'silencio':.2,'accesibilidad_salud':.2},
 # TODO(equipo): validar pesos de adulto mayor.
 'Adulto mayor': {'colegio':0,'espacios_verdes':.4,'conectividad':.6,'espacio_trabajo':0,'silencio':.6,'accesibilidad_salud':1.0},
 'Inversor': {'rentabilidad':.8,'precio_m2':.6,'conectividad':.2},
}
DESCRIPCIONES: dict[str,str] = {
 'Familia con hijos':'Colegios cerca, espacios verdes y lugar para todos.',
 'Profesional remoto':'Buena conexión, silencio y un rincón para trabajar.',
 'Pareja joven':'Cerca del transporte y de la vida de barrio.',
 'Adulto mayor':'Accesibilidad y centros de salud a mano.',
 'Inversor':'Compro para alquilar: rentabilidad y costo.',
}
assert set(PESOS_POR_DEFECTO)==set(ARQUETIPOS)
