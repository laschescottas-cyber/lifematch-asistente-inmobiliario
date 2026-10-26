# Guion de demostración · 3 a 5 minutos

Preparación: desde PowerShell activar `.venv`; para probar la aplicación, ejecutar `streamlit run app.py`. Tener instalado `google-genai`, una clave en variable de entorno y el modelo real habilitado. Mostrar primero la base sintética para evitar depender de la descarga de Properati; después explicar cómo se importa el CSV completo.

**0:00–0:30 | Catálogo.** Enseñar `data/muestra_demo.csv` (**sintético**) y `python scripts/cargar_catalogo.py data/muestra_demo.csv` sobre una base académica separada. Contar que los avisos de venta son candidatos y los de alquiler sirven como referencia estadística.

**0:30–1:30 | Familia.** Entrar en la app: perfil «Familia con hijos», compra, USD 260.000, Almagro, 2 ambientes; modificar pesos de colegio/parques y mostrar tarjetas, % LifeMatch y motivos. Explicar que los filtros se aplican antes del puntaje.

**1:30–2:30 | Inversor.** Inversor, capital USD 260.000, Almagro, rentabilidad objetivo 4%, horizonte 5 años. Mostrar **LifeMatch y rentabilidad en secciones diferentes**, mediana/alquiler y cantidad de avisos. Crear otro caso con barrio sin suficientes comparables para mostrar «sin dato»; eso no equivale a rendimiento 0%.

**2:30–3:00 | Cambia el ranking.** Reiniciar con otro perfil, por ejemplo «Profesional remoto», manteniendo el catálogo. Priorizar silencio/trabajo y contrastar con colegio/parques del perfil familiar.

**3:00–3:30 | Contingencia.** En PowerShell definir `$env:CATALOGO="demo"; $env:LLM="simulado"; $env:DEMO_LLM="falla"`; reiniciar Streamlit y buscar. Mostrar que aparece una explicación de plantilla **sin mensaje técnico**.

**3:30–4:00 | Sin resultados.** Buscar una zona inexistente y enseñar la sugerencia de ajustar presupuesto, zona o ambientes.

**4:00–5:00 | Eje 1 + Eje 2.** Para validar el Eje 1, desactivar demo y mostrar con un catálogo y **Gemini real configurado** que el texto se origina en `llm` (no alcanza con un cliente falso). Para el Eje 2, explicar el registro de IA, qué corrigió el equipo y enseñar el repositorio con commits incrementales y capturas reales de Trello.

Si la API real no está disponible, declarar expresamente que no se pudo probar la funcionalidad de IA real en esa demostración. No presentar la simulación como llamada a Gemini.
