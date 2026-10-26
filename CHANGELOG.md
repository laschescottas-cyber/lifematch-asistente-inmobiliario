# Registro de cambios

Todo cambio al proyecto queda anotado acá, con su fecha, el pull request que lo incorporó y la historia de usuario afectada. Lo más reciente va primero. El detalle técnico de cada cambio está en el pull request y en sus commits; el uso de IA en cada etapa se registra en [`docs/registro_uso_ia.md`](docs/registro_uso_ia.md).

Etiquetas: **Agregado** (funcionalidad nueva) · **Cambiado** (cambio de comportamiento) · **Corregido** (bug) · **Quitado** · **Documentación**.

---

## 25/10/2026 · PR #4 — Gemini rechazaba todos los pedidos por el plazo de espera

**Corregido**
- La app publicada nunca usaba Gemini: la API respondía `400 INVALID_ARGUMENT · Manually set deadline 8s is too short. Minimum allowed deadline is 10s.` El plazo HTTP se tomaba de `LLM_TIMEOUT_S` (8 s). Ahora se separan dos conceptos: `LLM_TIMEOUT_S` sigue siendo cuánto espera la app antes de usar la plantilla, y el plazo que se declara a la API nunca baja de 10 s. (HU-06, HU-07)
- La pista del registro para un error 400 culpaba siempre a la clave. Ahora solo lo hace si el motivo menciona la clave; si menciona el plazo, lo dice.
- 6 tests nuevos (cliente Gemini con un falso, sin red): 82 en total.

**Diagnóstico**
- La causa se encontró gracias al registro detallado del PR #3, en la primera búsqueda después del merge.
- Arreglo provisorio mientras tanto: `LLM_TIMEOUT_S = "12"` en Secretos. Con este PR deja de ser necesario, aunque no molesta.

## 25/10/2026 · PR #3 — Diagnóstico de errores de Gemini y errores ocultos al visitante

**Cambiado**
- Cuando Gemini rechaza un pedido, el registro de la app («Manage app» en Streamlit Cloud) muestra el código, el motivo y una pista de qué revisar (por ejemplo: `ClientError 404 NOT_FOUND … → revisá GEMINI_MODEL`). Antes solo decía `ClientError`. La clave nunca aparece en el registro: se enmascara. (HU-06, HU-07)
- Ante un error inesperado, los visitantes de la página ven solo un mensaje genérico; el detalle técnico queda únicamente en el registro (`.streamlit/config.toml`, `showErrorDetails = "none"`).
- `.gitignore` excluye `.streamlit/secrets.toml` para que una clave guardada en la PC nunca se suba a GitHub.
- 4 tests nuevos: 76 en total.

## 25/10/2026 · Configuración de la app publicada (Streamlit Cloud → Ajustes → Secretos)

- `CATALOGO = "demo"`, `LLM = "gemini"`, `GEMINI_MODEL = "gemini-3.5-flash-lite"`, `TOP_N = "5"` y la clave de Gemini (no se registra acá).
- Primera prueba: las explicaciones salieron con la plantilla de respaldo y el registro mostró `ClientError` (Gemini rechazó el pedido). Causa encontrada y corregida en el PR #4.

## 25/10/2026 · PR #2 — App publicada: catálogo de prueba con Gemini real

**Cambiado**
- La configuración `DEMO=1` se separa en dos independientes: `CATALOGO` (`properati` | `demo`) elige de dónde salen las propiedades y `LLM` (`gemini` | `simulado`) elige quién redacta la explicación. Antes no se podía publicar la app con el catálogo de prueba y la IA real. `DEMO=1` sigue funcionando como atajo. (HU-04, HU-06)

**Agregado**
- La app lee la configuración de **Settings → Secrets** de Streamlit Cloud. (HU-06)
- Si el catálogo de Properati está vacío, la app lo avisa en vez de responder «no hay propiedades que cumplan tus condiciones». (HU-03, HU-04)
- 8 tests nuevos (configuración y recorridos de interfaz): 72 en total.

**Quitado**
- 18 archivos `.pyc` compilados que se habían subido desde la web de GitHub.

**Documentación**
- README: tabla de configuraciones y sección «Publicación en Streamlit Cloud».
- Este `CHANGELOG.md`.

## 25/10/2026 · App publicada en Streamlit Cloud

- Publicación desde la rama `main`: https://lifematch-asistente-inmobiliario-les4zkedrmirvjywza4ysz.streamlit.app/

## 25/10/2026 · PR #1 — Incorporación del código y primera revisión

**Agregado**
- Base de código LifeMatch (Python, Streamlit, SQLite, Gemini) con tests por historia de usuario, tal como la generó el equipo con asistencia de IA.
- Tests de interfaz con `streamlit.testing`. (HU-01, HU-02, HU-03, HU-08)

**Corregido**
- La pantalla de resultados se rompía en las dos rutas (`TypeError`): `st.session_state.items` devolvía el método `dict.items`. (HU-08)

**Cambiado**
- Las explicaciones del top N se piden a Gemini en paralelo (`LLM_CONCURRENCIA`) en lugar de una por una. (HU-06)
- El prompt pide primero las variables que más aportaron y después las limitaciones. (HU-06)
- Cada tarjeta indica el origen de la explicación: Gemini, simulada o automática de respaldo. (HU-06, HU-07)

**Documentación**
- `docs/arquitectura.md`: capas, carpetas, flujo de integración con IA y diagrama ER de SQLite.
