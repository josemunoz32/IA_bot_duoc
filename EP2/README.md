# Proyecto de Agente IA - FinanChile Asesorías S.A.
**Evaluación Parcial 3: Observabilidad y Trazabilidad**

## Descripción del Proyecto
Este repositorio contiene el código fuente de "AsesorBot Pro", un agente inteligente funcional autónomo desarrollado para automatizar la atención al cliente en FinanChile. El proyecto integra herramientas de recuperación (RAG), memoria conversacional, cálculos de simulación de crédito y un panel completo de observabilidad.

## Estructura del Repositorio
*   `/agente/`: Contiene el core del Agente IA y configuración de LLMs.
*   `/vectorstore/`: Base de datos vectorial con normativas de la CMF.
*   `/cotizaciones/` y `/tickets/`: Archivos generados dinámicamente por las herramientas del agente.
*   `main.py`: Script principal para ejecutar el agente en modo interactivo y suites de prueba.
*   `dashboard.py`: Aplicación Streamlit para visualización de métricas y observabilidad.
*   `logs_agente.csv`: Registro de ejecución (trazabilidad) que alimenta el dashboard.
*   `informe_EP3.md`: Informe técnico con análisis y recomendaciones de optimización.

## Requisitos de Ejecución
1. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   pip install streamlit plotly pandas
   ```
2. Configurar variables de entorno: 
   Asegúrese de agregar sus API Keys en un archivo `.env` en la raíz del proyecto.
   ```
   OPENAI_API_KEY=tu_api_key_aqui
   ```

## Cómo ejecutar el Agente (Modo Interactivo y Pruebas)
Para iniciar la interfaz de chat en consola o ejecutar las pruebas automáticas:
```bash
python main.py
# Para correr la suite de testing automatizada:
python main.py test
```

## Cómo ejecutar el Dashboard de Observabilidad
Para visualizar las métricas de precisión, latencia y los registros de trazabilidad:
```bash
streamlit run dashboard.py
```
