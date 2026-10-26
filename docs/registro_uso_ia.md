# Registro del uso de IA durante el desarrollo

No completar etapas o revisiones que el equipo no realizó. Fecha y responsables reales antes de presentar.

| Fecha | Etapa | Herramienta de IA | Qué se le pidió (resumen del prompt) | Qué devolvió | Qué revisó o cambió el equipo | Quién |
|---|---|---|---|---|---|---|
| `[[COMPLETAR]]` | Codificación | GPT-6 | Generar el sistema desde el documento del TP, con Python/SQLite/Streamlit/Gemini y tests | Código fuente, tests, scripts, documentación y suite de pruebas | `[[COMPLETAR POR EL EQUIPO: qué verificaron, corrigieron o descartaron]]` | `[[COMPLETAR]]` |
| 25/10/2026 | Desarrollo / Pruebas | Claude (Anthropic) | Incorporar el código al repositorio, revisarlo contra el DOCX (puntos 1 a 5) y probar la app Streamlit real | Detectó que la pantalla de resultados se rompía (`st.session_state.items` devolvía el método `dict.items`); propuso paralelizar las llamadas a Gemini, test de UI con `streamlit.testing`, rótulo de origen de la explicación y `docs/arquitectura.md` | `[[COMPLETAR POR EL EQUIPO: qué revisaron y aceptaron/cambiaron]]` | `[[COMPLETAR]]` |
| `[[COMPLETAR]]` | Análisis | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` |
| `[[COMPLETAR]]` | Diseño | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` |
| `[[COMPLETAR]]` | Gestión | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` |
| `[[COMPLETAR]]` | Pruebas | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` | `[[COMPLETAR]]` |

## Análisis crítico (para completar con hechos del equipo)

1. ¿Qué usos concretos de IA mejoraron la calidad del trabajo y por qué?
2. ¿Qué sugerencia de IA fue incorrecta, incompleta o descartada, y qué decisión humana se tomó?
3. ¿Cambió cómo se repartieron tareas, escribieron tests o registraron cambios?
4. ¿Cuáles son las limitaciones visibles en LifeMatch y Gemini? ¿Qué harían con más tiempo?

**Eje 1:** la explicación contextual al usuario mediante Gemini debe demostrar una llamada real en la demo final (modo `DEMO=0`). **Eje 2:** hay que documentar los usos reales de IA en análisis, diseño, desarrollo, pruebas y gestión.
