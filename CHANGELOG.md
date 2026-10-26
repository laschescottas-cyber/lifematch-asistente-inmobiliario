# Registro de cambios

Todo cambio al proyecto queda anotado acá, con su fecha, el pull request que lo incorporó y la historia de usuario afectada. Lo más reciente va primero. El detalle técnico de cada cambio está en el pull request y en sus commits; el uso de IA en cada etapa se registra en [`docs/registro_uso_ia.md`](docs/registro_uso_ia.md).

Etiquetas: **Agregado** (funcionalidad nueva) · **Cambiado** (cambio de comportamiento) · **Corregido** (bug) · **Quitado** · **Documentación**.

---

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
