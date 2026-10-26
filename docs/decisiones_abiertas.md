# Observaciones al diseño y decisiones abiertas

1. **`Propiedad.id`:** el diagrama de clases original lo representa como entero, pero el `id` de Properati se conserva como **texto**; documentar el ajuste del diagrama.
2. **DER de Match:** `Match.detalle` y `variables_sin_dato` **no aparecen como columnas** ni se guardan; se recalculan durante cada búsqueda.
3. **Horizonte:** `PerfilInversor.horizonte_anios` es informativo y no afecta LifeMatch ni las rentabilidades.
4. **Ambientes:** `pref.ambientes` significa cantidad **mínima**, no igualdad.
5. **Pesos y keywords:** los pesos de Profesional remoto, Pareja joven, Adulto mayor y las palabras clave de entorno son propuestas; deben validarse con el equipo.
6. **Umbral estadístico:** `MIN_AVISOS_ALQUILER=5` es provisional. En propiedades sin comparables el resultado es «sin dato».
7. **Dataset completo:** verificar valores reales de `price_period`, `currency` y `property_type` de alquileres, sus tasas de campos faltantes y el tiempo de importación a gran escala.
8. **Actualización del TP:** Preferencia.operacion, Match.id_preferencia, Rentabilidad y PerfilInversor ya figuran en diagramas; actualizar los diagramas con los métodos que incorpora el código si el docente acepta el ajuste.
9. **Ranking e inversión:** la rentabilidad estimada no considera expensas, reparaciones, vacancia, impuestos, actualización de alquileres ni calidad del barrio. No usar como asesoramiento de inversión.
10. **Normalización semántica:** menciones del anuncio no son distancias físicas. Conectividad significa transporte, no internet. «Vida de barrio» no tiene variable independiente en el diseño aprobado.
11. **Concurrencia y seguridad:** el hilo daemon previene bloquear la búsqueda cuando la API no responde, pero múltiples timeouts simultáneos pueden dejar hilos vivos hasta el retorno de la conexión. Valorar límites de concurrencia al escalar.
12. **Carga histórica:** `ON CONFLICT(id) DO UPDATE` equivale a un upsert idempotente sin borrar la fila y sin invalidar matches referenciados. Se aparta de la redacción literal `INSERT OR REPLACE` por integridad referencial.
13. **Validación de UI:** faltan pruebas manuales del recorrido completo en Streamlit y en Windows 11/Python 3.12; se probaron por separado la lógica de pantallas y el backend en un entorno Python 3.13.
14. **IA real:** confirmar clave, modelo habilitado, latencia, respuesta y facturación del SDK `google-genai`. Los tests no conectan a internet; la demo sin clave es simulada.
15. **Trello, GitHub y cierre:** faltan capturas de tres momentos auténticos del tablero, repositorio publicado, historia de commits del equipo y el registro/análisis crítico de IA en cinco etapas. No se pueden fabricar desde el código.
16. **CSV de prueba:** `data/muestra_demo.csv` es enteramente sintético y no reemplaza el dataset Properati histórico. Las mediciones obtenidas sobre este CSV son demostrativas, no reales.
