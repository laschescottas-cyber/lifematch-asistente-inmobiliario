# Trazabilidad de requisitos, clases, pruebas y pantallas

| HU | Funcionalidad | Clases y módulos | Pruebas | Interfaz |
|---|---|---|---|---|
| HU-01 | Elegir 5 perfiles / objetivo | Usuario, `arquetipos.py` | `test_hu01_arquetipo.py` | `ui/pantallas.py` / perfil |
| HU-02 | Ruta de preguntas / validar / resumen editable | Preferencia, PerfilInversor, `ui/logica.py` | `test_hu02_formulario.py` | datos, prioridades, resumen |
| HU-03 | Filtros duros / sin resultados | Propiedad, FiltrosDuros, Catalogo | `test_hu03_filtros.py`, `test_integracion.py` | resultados y sin resultados |
| HU-04 | Normalizar CSV, venta/alquiler y persistir | Catalogo, RepositorioSQLite, ResumenCarga | `test_hu04_catalogo.py` | carga por CLI / catálogo |
| HU-05 | LifeMatch y rentabilidad separada | MotorMatching, EstimadorRentabilidad, Rentabilidad, Match | `test_hu05_matching.py`, `test_hu05_rentabilidad.py`, `test_integracion.py` | resultados y detalle |
| HU-06 | Explicaciones Gemini a partir de datos del match | ClienteGemini, ServicioExplicacionIA, Explicacion | `test_hu06_explicacion.py`, `test_integracion.py` | detalle |
| HU-07 | Timeout/errores/vacío → respaldo | PlantillaRespaldo, ServicioExplicacionIA | `test_hu07_respaldo.py` | detalle sin error técnico |
| HU-08 | Tarjetas y orden | ItemResultado, `ui/logica.py` | `test_hu08_resultados.py` | resultados / ordenar / detalle |

La suite comprueba clases, reglas de negocio, persistencia y utilidades de pantalla **sin ejecutar interacciones visuales de Streamlit**. Los criterios de aceptación relativos a mostrar controles, editar sobre la interfaz o captar eventos deben validarse manualmente. Los tests de Gemini usan fakes: **no prueban** la API real. No se debe presentar esto como cobertura E2E de navegador.

## Casos numéricos de control

- Vivir 6 variables: **86,8** (`test_caso_control_86_8`).
- Familia 3 variables: **80,0** (`test_ejemplo_familia_80`).
- Inversor completo: **89,5** (`test_ejemplo_inversor_89_5`).
- Inversor sin rentabilidad: **94,0** (`test_variable_sin_dato_se_excluye_y_renormaliza`).

## Revisión manual obligatoria

Confirmar las 8 pantallas de los wireframes, búsqueda correcta desde Streamlit, condiciones obligatorias, sliders, mensajes al omitir campos, cambio de perfil alterando ranking, fallback al simular un error y registros SQLite. Comparar contra cada captura/diagrama del documento base.
