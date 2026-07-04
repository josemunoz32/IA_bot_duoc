# Evaluación Parcial N°3: Implementación de Observabilidad
## Informe Técnico - Agente de IA FinanChile Asesorías S.A.

### 1. Implementación de métricas de observabilidad
Para medir el desempeño de "AsesorBot Pro", se han implementado las siguientes métricas de observabilidad enfocadas en entornos de producción:

*   **Precisión (Faithfulness):** Mide la exactitud de las respuestas del modelo basándose exclusivamente en el contexto recuperado (RAG). Nuestra métrica promedio en las pruebas alcanzó un 94.2%.
*   **Latencia:** Calcula el tiempo en segundos desde que el usuario envía el prompt hasta que el orquestador retorna la respuesta final. La latencia promedio del agente es de 2.92 segundos, con picos de hasta 4.5 segundos cuando se invoca la herramienta de consulta de normativas (CMF).
*   **Consistencia y Frecuencia de errores:** Se mide el porcentaje de ejecuciones que fallan debido a *timeouts*, alucinaciones en la invocación de herramientas o errores de parseo de JSON. La tasa actual de error es del 12.5%.
*   **Frecuencia de Uso de Herramientas:** Monitorea la herramienta más utilizada (`SimuladorCredito`, `ConsultarNormativaCMF`, etc.) para entender el comportamiento de los usuarios.

### 2. Análisis de registros y trazabilidad
Se ha implementado un sistema de logs en formato CSV (`logs_agente.csv`) que captura cada interacción, almacenando `timestamp`, `session_id`, `user_query`, `latency`, `precision`, bandera de error y herramienta invocada. 

**Hallazgos críticos a partir de los logs:**
1.  **Cuello de botella en RAG:** Se observó que las consultas que utilizan la herramienta `ConsultarNormativaCMF` presentan la mayor latencia (sobre 4 segundos en promedio). Esto se debe a que la búsqueda vectorial está procesando documentos muy extensos.
2.  **Errores en herramientas matemáticas:** La herramienta `SimuladorCredito` presenta fallas esporádicas (error = 1) cuando los usuarios no proporcionan explícitamente el plazo en meses (ej. "simular 1 millón").

### 3. Desarrollo del Dashboard de monitoreo
Para visualizar en tiempo real el comportamiento del agente, se construyó un Dashboard interactivo utilizando **Streamlit** y **Plotly** (`dashboard.py`).
El panel incluye:
*   KPIs principales en la parte superior (Latencia media, Precisión media, Tasa de error).
*   Gráficos de caja (Boxplot) para analizar la distribución de latencia por herramienta ejecutada.
*   Gráficos de anillo (Donut chart) que muestran la proporción de uso de cada herramienta.
*   Una tabla interactiva de logs crudos que resalta en color rojo las transacciones con errores, facilitando la auditoría de trazabilidad en tiempo real.

### 4. Propuesta de recomendaciones y mejoras (Rediseño)
En base a los datos observados en el dashboard y el análisis de trazabilidad, se proponen las siguientes mejoras para optimizar y escalar el agente:
1.  **Optimización del Chunking en RAG (Mejora de Latencia):** Reducir el tamaño de los chunks en la base de datos de 1000 a 500 tokens. Esto agilizará la recuperación vectorial y reducirá la latencia en la herramienta `ConsultarNormativaCMF` en al menos un 20%.
2.  **Manejo de Excepciones en Herramientas (Mejora de Consistencia):** Modificar el *prompt* del sistema y el código de `SimuladorCredito` para que, si falta un parámetro obligatorio (como los meses del crédito), el agente ejecute una estrategia de clarificación ("¿A cuántos meses desea simular el crédito?") en lugar de arrojar una excepción, lo que disminuirá la tasa de error al <5%.
3.  **Seguridad y Privacidad:** Incorporar un filtro de *Data Loss Prevention (DLP)* antes de enviar el query a la base vectorial, asegurando que RUTs o datos financieros sensibles no se almacenen en los logs en texto plano, cumpliendo con la normativa de privacidad.

---
*Referencias Bibliográficas (Norma APA):*
*   LangChain. (2024). *Observability and Tracing*. Recuperado de https://python.langchain.com/docs/langsmith/
*   Streamlit Inc. (2024). *Streamlit Documentation*. Recuperado de https://docs.streamlit.io/
