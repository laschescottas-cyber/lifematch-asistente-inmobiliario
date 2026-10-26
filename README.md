# LifeMatch · Asistente Inmobiliario Inteligente

Trabajo Práctico Integrador — Desarrollo de Software con Inteligencia Artificial, IFTS Nº 12, Grupo 5 (2026).

**Objetivo:** recomendar inmuebles por la intención de búsqueda y el perfil de vida o inversión. Dos recorridos: **vivir** (compra/alquiler, cuatro perfiles) e **invertir** (compra para alquilar).

El sistema combina: (1) filtros duros, (2) índice reproducible **LifeMatch** (0–100), (3) estimador estadístico de rentabilidad bruta para inversor, (4) explicación mediante la API de **Gemini** con **plantilla de respaldo**. LifeMatch es un algoritmo determinístico, no un modelo entrenado; la rentabilidad tampoco es ML. La integración con Gemini es la funcionalidad de IA auténtica (HU-06).

## Requisitos

- **Windows 11 y Python 3.12** (la suite se ejecutó en el entorno de desarrollo también con Python 3.13; verificar específicamente Python 3.12 en la PC del equipo).
- Acceso a internet y clave de Gemini para demostrar la explicación real con LLM; para el modo demo no hacen falta.
- Dataset Properati Argentina CSV para usar los avisos históricos reales.

## Instalación, PowerShell

Desde la raíz del repositorio:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea el script, ejecutar en esa terminal `Set-ExecutionPolicy -Scope Process Bypass` antes de activarlo; no hace falta cambiar la política global.

## Dataset histórico Properati

1. Accedé al dataset <https://www.kaggle.com/datasets/alejandroczernikier/properati-argentina-dataset>.
2. Descargá manualmente el CSV completo de Argentina y renombrá **solo el archivo** como `properati.csv`.
3. Guardalo en `data/properati.csv`; **no lo subas a Git**.
4. Desde la raíz del proyecto, cargalo en SQLite:

```powershell
python scripts/cargar_catalogo.py data/properati.csv
```

El importador procesa por lotes de 5000, tolera BOM, filas entre comillas, descripciones multilínea y datos incompletos; carga compras y alquileres sin duplicar avisos al repetir la importación. El archivo debe incluir las 25 columnas declaradas en `docs/regla_normalizacion_catalogo.md`. La descarga **no se realiza automáticamente**. Para el lote completo, monitoreá tiempo y espacio en disco (no se verificó aquí el rendimiento de millones de filas).

## Configurar Gemini (explicación real)

Obtené una clave válida en Google AI Studio e indicá el modelo **disponible para tu cuenta**. No escribas la clave en el código ni la subas a Git. En PowerShell, para la sesión actual:

```powershell
$env:GEMINI_API_KEY = "TU_CLAVE_PERSONAL"
$env:GEMINI_MODEL = "EL_MODELO_HABILITADO_PARA_TU_CUENTA"
$env:LLM_TIMEOUT_S = "8"
$env:TOP_N = "10"
$env:LLM_CONCURRENCIA = "4"   # bajar a 1-2 si el plan gratuito de Gemini devuelve 429
$env:DB_PATH = "data/inmobiliaria.db"
```

El SDK usado es `google-genai`, mediante `genai.Client(api_key=...)` y `client.models.generate_content(model=...,contents=...)`; el timeout también está protegido por un hilo daemon desde el servicio XAI. Si la clave/modelo son inválidos, la API falla o se agota el tiempo, el usuario recibe una **explicación de respaldo**, sin ver una excepción. Validá el acceso real de forma manual (nunca desde pytest):

```powershell
python scripts/probar_gemini.py
```

## Ejecutar aplicación

```powershell
streamlit run app.py
```

Secuencia: seleccionar perfil → condiciones → prioridades (sliders) → resumen editable → resultados → detalles. Las fotos y distancias reales no existen en la fuente histórica, así que no se inventan. El `TOP_N` indica cuántos candidatos de mayor LifeMatch se explican y guardan por búsqueda. Las explicaciones se piden a Gemini en paralelo (`LLM_CONCURRENCIA`), así que el tiempo de búsqueda no crece en proporción a `TOP_N`; para la demo en vivo conviene `TOP_N=5`.

## Catálogo y proveedor de IA (dos configuraciones independientes)

| Variable | Valores | Qué decide |
|---|---|---|
| `CATALOGO` | `properati` (por defecto) · `demo` | De dónde salen las propiedades: la base cargada con `scripts/cargar_catalogo.py` o el catálogo **sintético** `data/muestra_demo.csv` |
| `LLM` | `gemini` (por defecto) · `simulado` | Quién redacta la explicación: la API real de Gemini o `ClienteDemo`, sin red |
| `DEMO_LLM` | `ok` · `falla` | Solo con `LLM=simulado`: `falla` fuerza el plan de respaldo (HU-07) |
| `DEMO` | `1` | Atajo compatible: equivale a `CATALOGO=demo` + `LLM=simulado`. Si se definen `CATALOGO` o `LLM`, esas ganan |

Combinaciones habituales:

```powershell
# Sin internet: catálogo de prueba + IA simulada
$env:CATALOGO = "demo"; $env:LLM = "simulado"; streamlit run app.py

# Catálogo de prueba + Gemini real (lo que usa la app publicada)
$env:CATALOGO = "demo"; $env:LLM = "gemini"; streamlit run app.py

# Forzar el plan de respaldo
$env:CATALOGO = "demo"; $env:LLM = "simulado"; $env:DEMO_LLM = "falla"; streamlit run app.py
```

Con `LLM=simulado` la explicación **no** proviene de una IA real y la tarjeta lo indica («Modo demo: explicación simulada»). Si `CATALOGO=properati` y la base está vacía, la app lo avisa en vez de responder «no hay propiedades que cumplan tus condiciones».

## Publicación en Streamlit Cloud

La app se publica desde la rama `main`: cada cambio que llega a `main` se republica solo. La configuración va en **Settings → Secrets** de la app (formato TOML) y **nunca** en el repositorio:

```toml
CATALOGO = "demo"
LLM = "gemini"
GEMINI_API_KEY = "la clave personal"
GEMINI_MODEL = "el modelo habilitado para la cuenta"
TOP_N = "5"
```

`ui/pantallas.py` copia esas claves a variables de entorno al iniciar, así la misma configuración funciona en la PC y en la nube. Sin clave o con la API caída, la app sigue funcionando con la explicación de respaldo. El CSV completo de Properati no se sube a GitHub, por eso la app publicada usa el catálogo de prueba.

Los cambios se registran en [`CHANGELOG.md`](CHANGELOG.md) y entran a `main` mediante pull requests.

Demo equivalente por consola (útil para ensayar y auditar resultados):

```powershell
python scripts/demo_en_vivo.py
```

El script usa una base temporal y ejecuta familia, inversor, contraste de perfiles, falla forzada y búsqueda sin resultados.

## Pruebas

```powershell
python -m pytest -q
```

La suite usa bases de datos temporales y clientes de IA falsos. `tests/test_ui_streamlit.py` recorre las pantallas reales de la app con `streamlit.testing` (modo demo) hasta los resultados de las rutas vivir e invertir y la pantalla sin resultados. **Nunca consume créditos de Gemini**, ni requiere internet o descargar Properati. Incluye los casos numéricos de LifeMatch **86,8 / 80,0 / 89,5 / 94,0**. Revisá el resultado real final y la cobertura en `docs/trazabilidad.md`.

## Arquitectura

```text
Streamlit (HU-01/02/08)
    ↓
Backend.buscar → Catalogo.buscar → Repositorio SQLite → FiltrosDuros (HU-03/04)
    ↓
MotorMatching → LifeMatch
    ├─ Para vivir: variables de entorno extraídas del aviso
    └─ Inversor: EstimadorRentabilidad + mediana de precio/m² (HU-05)
    ↓
ServicioExplicacionIA → ClienteGemini (HU-06)
    └─ timeout / error / vacío → PlantillaRespaldo (HU-07)
    ↓
Match + rentabilidad + explicación → SQLite → tarjetas / detalle
```

Detalle completo de capas, carpetas, flujo de integración con Gemini y esquema SQLite (diagrama ER) en [`docs/arquitectura.md`](docs/arquitectura.md).

`src/inmobiliaria/modelos.py` contiene las entidades del TP. `repositorio.py` guarda el DER en SQLite. `catalogo.py` transforma y carga. `ui/logica.py` ofrece utilidades puras y probables; `ui/pantallas.py` presenta la aplicación.

## Limitaciones de los datos

La muestra analizada en el trabajo académico incluye avisos de **2019–2020**, con **precios pedidos** y no precios de operaciones efectivas: no representan el mercado actual. Algunos campos de superficie y ubicación pueden estar vacíos o inconsistentes; `lat/lon` pueden venir intercambiados, `price_period` a veces figura en ventas y `rooms` puede diferir del título. No hay fotografías ni distancias reales a transporte, hospitales, colegios o parques. Por eso **menciones de palabras clave ≠ cercanía real**. La rentabilidad es **bruta, estimada y no garantizada**, sin descontar gastos/impuestos/vacancia.

## Uso de IA en el desarrollo — Eje 2

Se generó una base de código, tests y documentación con asistencia de GPT-6 a partir del TP y un prompt técnico detallado. **El equipo debe revisar, comprender, corregir y validar** el código, y completar `docs/registro_uso_ia.md` indicando las decisiones reales, cambios y responsables. No declarar pruebas manuales o revisiones no efectuadas. Para la entrega final el docente también exige registro de IA en análisis, diseño, gestión y pruebas, más reflexión crítica propia.

## Git / Trello

Registrar commits graduales usando `[HU-0X]` y, para HU-05, HU-06 y HU-07, `[IA]`. Ejemplos:

```text
[HU-04] Normalización del catálogo Properati
[HU-05][IA] LifeMatch y rentabilidad estadística
[HU-06][IA] Integración Gemini con servicio XAI
[HU-07][IA] Timeout y plantilla de contingencia
[HU-08] Tarjetas de resultados y detalle
```

No simular un historial de commits: registrar los cambios a partir de ahora. En Trello registrar **tres momentos reales** con capturas distintas (no fabricar el progreso).

## Seguridad y buenas prácticas

`.gitignore` excluye `.env`, las bases SQLite, el CSV completo y el entorno virtual. `.env.example` contiene variables vacías. No se envían nombre ni email de usuario al prompt del LLM; se usan únicamente datos estructurados del match. El sistema guarda un usuario genérico `Visitante`, sin pedir email. El estimador filtra por barrio, tipo, moneda compatible y períodos mensuales; la cantidad mínima de avisos comparables es configurable.

## Antes de entregar al docente

Validar el **SDK y la API reales**, verificar valores reales de moneda/periodicidad en el CSV completo, probar con Python 3.12/Windows 11 y realizar la demo de Streamlit en una PC del equipo. Revisar los wireframes y el DER del DOCX, documentar el uso real de IA en cinco etapas, completar tres capturas auténticas de Trello y configurar un repositorio GitHub público/privado elegido por el grupo.
