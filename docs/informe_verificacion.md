# Informe de verificación · 23 de octubre de 2026

## Resultados ejecutados en el entorno de creación

- **58 tests automáticos aprobados** con `python -m pytest -q` sobre Python 3.13.5. Las pruebas cubren reglas de dominio, CSV normal/entrecomillado/multilínea, normalización, persistencia, filtros, control LifeMatch, rentabilidad, timeout/errores/ausencia de respuesta del LLM, resultados e integración de backend.
- `python -m compileall -q src app.py scripts` sin errores de sintaxis.
- `python scripts/demo_en_vivo.py` ejecutado correctamente con 14 avisos sintéticos (8 ventas, 6 alquileres). Se comprobaron búsqueda de familia, inversor, inversor en barrio sin alquileres comparables (sin dato), perfil remoto, fallback forzado y sin resultados.
- La SDK `google-genai` y su sintaxis se contrastaron con la documentación oficial vigente; **no se realizó llamada real a Gemini** por falta de clave habilitada suministrada.
- **Streamlit no pudo instalarse** en este entorno por falta de conectividad de paquetes: la UI existe y compila, pero **no hubo smoke test gráfico**.
- No se cargó el CSV completo de Properati; solo se utilizaron fixtures y datos sintéticos.

## Fases del desarrollo

1. **FASE 1 LISTA**: base del proyecto, configuración, modelos y tests.
2. **FASE 2 LISTA**: SQLite, normalización, carga por lotes, filtros y tests.
3. **FASE 3 LISTA**: arquetipos, LifeMatch, rentabilidad y casos de control.
4. **FASE 4 LISTA**: cliente de Gemini, XAI, timeout y respaldo.
5. **FASE 5 LISTA**: backend, resultados y persistencia con tests.
6. **FASE 6 CÓDIGO LISTO / VALIDACIÓN GRÁFICA PENDIENTE**: Streamlit, demo, utilidades de UI.
7. **FASE 7 LISTA**: README, documentación, guion demo, scripts, registro IA y decisiones pendientes.
8. **FASE 8 REVISADA / VERIFICACIONES EXTERNAS PENDIENTES**: checklist detallada abajo.

## Autoverificación de la sección 16 del prompt

| Nº | Estado | Evidencia / observación |
|---|---|---|
| 1. Nombres de clases y columnas del TP | **Sí** (con adaptación indicada) | `src/inmobiliaria/modelos.py`, `repositorio.py`; `id` de Propiedad se modeló como texto |
| 2. Un test por criterio Gherkin HU-01–HU-08 | **Parcial** | 58 tests cubren la lógica y el backend; los criterios de interacción visual de Streamlit requieren pruebas de UI/manuales |
| 3. Casos 86.8, 80.0, 89.5, 94.0 | **Sí** | `tests/test_hu05_matching.py` |
| 4. Nombre/email fuera de prompt, clave por entorno | **Sí a nivel de código** | `Match.generar_explicacion_request`, `ServicioExplicacionIA`, `ClienteGemini`, `.env.example` y tests de privacidad |
| 5. API falla/timeout/vacío sin mensaje técnico al usuario | **Sí a nivel de servicio** | `explicacion/servicio.py` y `test_hu07_respaldo.py`; pendiente comprobar interacción Streamlit |
| 6. Rentabilidad separada, «sin dato» | **Sí** | `rentabilidad.py`, `ui/pantallas.py`, tests + demo de Caballito |
| 7. CSV robusto y streaming | **Sí para fixtures; rendimiento masivo pendiente** | `catalogo.py`, `test_hu04_catalogo.py`; sin prueba del dataset completo |
| 8. README, demo, trazabilidad, registro IA | **Sí** | `README.md`, `docs/guion_demo.md`, `docs/trazabilidad.md`, `docs/registro_uso_ia.md` |
| 9. No verificado | **Pendiente** | Gemini real con clave, Streamlit real, Windows/Python 3.12, dataset completo, rendimiento en millones de avisos, publicación GitHub y 3 capturas auténticas de Trello |

**Importante:** la funcionalidad de IA obligatoria de la consigna requiere una demostración **real** contra Gemini, además de esta validación sin API. El modo demo es un simulador y se presenta como tal.

## Revisión del 25 de octubre de 2026 (incorporación al repositorio)

- **Streamlit sí se ejecutó** (1.66, Python 3.13, modo `DEMO=1`), recorriendo en navegador las rutas «Familia con hijos» e «Inversor» de punta a punta.
- **Bug encontrado y corregido:** la pantalla de resultados lanzaba `TypeError: object of type 'method' has no len()`. `st.session_state.items` devuelve el método `items()` del estado, no la lista guardada. Se renombró la clave a `resultados`. Los 58 tests previos no lo detectaban porque no ejecutaban la interfaz.
- **Nuevo:** `tests/test_ui_streamlit.py` (5 tests con `streamlit.testing`), que falla si se reintroduce el bug.
- **Rendimiento con Gemini real:** las explicaciones del top N se generaban en serie (hasta `TOP_N × LLM_TIMEOUT_S` en el peor caso). Ahora se piden en paralelo (`LLM_CONCURRENCIA`, por defecto 4), con un test que lo verifica.
- **Interfaz:** cada tarjeta indica el origen de la explicación (Gemini, simulada en modo demo, o automática de respaldo). La etiqueta «Capital máximo de compra (USD)» ya no fija la moneda, y la superficie se muestra como «60 m²».
- **Prompt:** se agregó la consigna del borrador del DOCX: primero las variables que más aportaron y después las limitaciones.
- Resultado: **64 tests aprobados**. Sigue **sin probarse la llamada real a Gemini**: este entorno no tiene salida a la API.
