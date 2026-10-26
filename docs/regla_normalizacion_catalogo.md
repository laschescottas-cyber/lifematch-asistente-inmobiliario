# HU-04 · Reglas de normalización de Properati

## Fuente

Properati Argentina Dataset, publicado por alejandroczernikier en Kaggle. Uso académico: avisos de la muestra histórica 2019–2020, no cotizaciones actuales ni precios de cierre.

## Columnas originales

`id, ad_type, start_date, end_date, created_on, lat, lon, l1, l2, l3, l4, l5, l6, rooms, bedrooms, bathrooms, surface_total, surface_covered, currency, price_period, title, description, property_type, operation_type, price`

Se mantienen sin renombrar en la tabla `propiedad`; `precio_m2` es un derivado nuevo. La clave `id` se almacena como `TEXT`, pues el dataset no asegura entero.

## Transformaciones

| Situación | Tratamiento |
|---|---|
| BOM | `utf-8-sig` |
| Un registro llega como un solo campo CSV con comillas duplicadas | Se reparsea usando `csv.reader` y `StringIO`, también con multilíneas |
| Fila con número de columnas distinto de 25 | Se descarta y cuenta |
| Falta id, precio positivo, moneda, operación, l3 o rooms | Se descarta y cuenta |
| `lat`/`lon` invertidos (lat fuera de [-56,-21], lon dentro) | Se intercambian |
| Mojibake típico `Ã` o `â€` | Intentar `encode('latin-1').decode('utf-8')`; ante error preservar original |
| No hay `surface_covered` | Usar `surface_total` para precio/m²; si tampoco hay, conservar con `precio_m2=None` |
| `price_period` en Venta | Ignorar (guardar NULL) |
| `rooms` difiere del texto | Prevalece `rooms` estructurado y ambientes = `int(rooms)` |
| Venta y Alquiler | Ambos se mantienen, diferenciados por `operation_type` |
| `end_date=9999-12-31` | Preservar como fecha textual de aviso sin baja |

`ResumenCarga(leidos,validos,descartados,completados)` cuenta los registros; `completados` incluye los avisos con superficie no disponible o coordenadas corregidas. El CSV se procesa en bloques configurables, y UPSERT por `id` evita duplicar y permite preservar referencias SQLite de matches históricos.

### Derivados

- `id_propiedad = id` como texto.
- `precio = price`; `moneda = currency`.
- `ubicacion = l2, l3, l4, l5, l6` sin valores vacíos.
- `ambientes = int(rooms)`.
- `precio_m2 = price / (surface_covered >0 ? surface_covered : surface_total)` cuando hay superficie válida.
- `caracteristicas` extraídas desde `title + description`, valor `1.0` solo por palabra encontrada, en otro caso `0.0`.

### Tabla de palabras clave (propuestas, validar con el equipo)

| Variable | Términos |
|---|---|
| `colegio` | colegio*, escuela*, jardin de infantes, nivel inicial, primaria, secundaria, universidad* |
| `espacios_verdes` | parque*, plaza*, espacio verde, espacios verdes, jardin, patio, bosque*, reserva ecologica |
| `conectividad` | subte, metrobus, tren, colectivo*, estacion*, premetro, medios de transporte, transporte publico |
| `espacio_trabajo` | home office, oficina*, escritorio, espacio de trabajo, apto profesional, coworking |
| `silencio` | tranquil*, silenc*, contrafrente, pasaje |
| `accesibilidad_salud` | ascensor*, rampa*, discapacitad*, accesible, hospital*, clinica*, sanatorio*, centro de salud |

`*` permite prefijo de palabra, no búsqueda parcial arbitraria; el resto exige palabra o frase completa. Se normalizan mayúsculas, tildes y espacios. `conectividad` se refiere **solo al transporte mencionado**, no a conexión a internet. Si no se menciona una condición se marca `0.0`, pero la interfaz debe decir **«el aviso no lo menciona»**, nunca inferir que la característica no existe.

## Métricas sin dato

Rentabilidad y mediana de precio/m² requieren muestra estadística suficiente. Si faltan comparables o superficie, la variable queda **sin dato**, excluida y con renormalización de LifeMatch, sin penalizar al aviso. En contraste, la ausencia de mención de una característica de entorno puntúa 0.0 (ausencia de evidencia a favor).

## Revisión pendiente

TODO(equipo): validar las palabras clave, `MIN_AVISOS_ALQUILER` y los valores reales de `price_period`, `currency`, `property_type` del CSV completo. Evitar confundir rentabilidad bruta con neta y cercanía real con una palabra en un anuncio.
