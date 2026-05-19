# Informe Técnico: Agente Funcional Autónomo (AsesorBot Pro)

**Autor:** José Muñoz  
**Organización:** FinanChile Asesorías S.A.  
**Curso:** Ingeniería de Soluciones con Inteligencia Artificial  
**Evaluación:** Evaluación Parcial N°2 (EP2)  

---

## 1. Introducción y Resumen del Proyecto

Este informe técnico describe el diseño, la implementación y la validación del **AsesorBot Pro v2.0**, un agente conversacional inteligente y autónomo desarrollado para la empresa de asesorías financieras **FinanChile Asesorías S.A.**

El objetivo principal de esta segunda entrega (EP2) fue transformar el sistema básico de recuperación de información (RAG) de la EP1 en un sistema conversacional interactivo completo. El agente no solo recupera textos relevantes de políticas e información comercial, sino que además gestiona variables en tiempo real a través de **memoria persistente a corto plazo**, realiza cálculos financieros exactos mediante código en Python (evitando las alucinaciones matemáticas características de los LLM) y toma decisiones autónomas de derivación hacia personal de soporte humano cuando se detecta frustración en el usuario o consultas que exceden el alcance del bot. 

Toda la solución se implementó utilizando el framework **LangChain** y está configurada para operar con el dialecto del español de Chile, respetando las regulaciones vigentes de la Comisión para el Mercado Financiero (CMF).

---

## 2. Justificación de la Arquitectura y Frameworks Seleccionados

### 2.1 Elección de LangChain como Orquestador
Para construir un agente que tome decisiones en tiempo real, programar scripts directos usando la API básica de OpenAI suele quedarse corto, especialmente al manejar estados conversacionales complejos. Seleccioné **LangChain** por las siguientes razones técnicas:
*   **Gestión del Patrón ReAct (Reasoning and Acting):** Permite configurar un agente interactivo que decide qué herramientas invocar en base a las preguntas del cliente, coordinando de manera automática el flujo de ejecución.
*   **Abstracción de herramientas:** Facilita la creación y conexión de funciones en Python puro (tools) al modelo de lenguaje, definiendo claramente los parámetros que requiere cada herramienta mediante descripciones precisas.
*   **Seguridad y control de bucles:** Configurando `max_iterations=10` en el `AgentExecutor` se previene que el agente entre en llamadas infinitas en caso de respuestas ambiguas del modelo, evitando cobros excesivos en la API.

### 2.2 Motor de Inferencia y Embeddings
*   **Modelo LLM (GPT-4o):** Se utilizó el modelo `gpt-4o` mediante los endpoints de inferencia de GitHub Models. Este modelo demostró capacidades avanzadas de razonamiento lógico, seguimiento de instrucciones estrictas del System Prompt y traducción impecable de dialectos.
*   **Base Vectorial (FAISS):** Se continuó utilizando la base de datos indexada con **FAISS** y el modelo de embeddings `text-embedding-3-small` de la EP1, lo que permite buscar similitudes semánticas muy rápido y sin consumo excesivo de recursos locales.

---

## 3. Diseño e Implementación del Sistema

### 3.1 Arquitectura del Agente
El flujo de datos del agente se diseñó para separar de manera clara la interfaz de consola, el núcleo del agente conversacional y las herramientas especializadas:

```
[Cliente (CLI / main.py)] <---> [Agente Core (core.py)] <---> [Memoria (memory.py)]
                                        |
                             +----------+----------+
                             |   H E R R A M I E N T A S   |
                             +----------+----------+
                    +--------+-----+----+--------+
                    |              |             |
                    v              v             v
             [Consulta RAG]   [Calculadora] [Escritura]  [Escalación]
               (FAISS)         (Python)      (Cotiz/Tkts) (Humanos)
```

### 3.2 Implementación de las Herramientas Autónomas
El agente cuenta con cuatro herramientas que implementan la lógica de negocio y aseguran que no existan alucinaciones de datos:

1.  **Consulta RAG (`obtener_informacion_financhile`):** Ejecuta la búsqueda semántica en la base de datos vectorial FAISS. Recupera la información de productos y políticas internas, asegurando inyectar metadatos de origen para que el agente cite la fuente de forma explícita al final de su respuesta (ej. `[Manual de Productos Financieros]`).
2.  **Calculadora Financiera (`simular_operacion_financiera`):** Es una herramienta crítica para evitar alucinaciones matemáticas. Realiza operaciones numéricas deterministas usando algoritmos en backend:
    *   *Crédito de Consumo:* Calcula la cuota aplicando el sistema de **Amortización Francesa**:
        $$R = P \times \frac{i(1+i)^n}{(1+i)^n - 1}$$
        (Donde $R$ es la cuota, $P$ el monto, $i$ la tasa mensual fija de 1.8% y $n$ las cuotas).
    *   *Crédito Hipotecario:* Convierte a UF (usando $38.453,21 CLP por UF), exige un pie mínimo obligatorio del 20% y simula el saldo con una tasa de 4.25% anual.
    *   *Ahorro e Inversión:* Realiza proyecciones usando fórmulas de interés compuesto para tres fondos diferentes (Cuenta Máx, Conservador y Crecimiento), inyectando de forma obligatoria la advertencia regulatoria de la CMF.
3.  **Escritura Local (`guardar_documento_cliente`):** Permite registrar propuestas formales y tickets en disco (carpetas `EP2/cotizaciones/` y `EP2/tickets/`). Solicita explícitamente el RUT y nombre antes de escribir para asegurar la integridad de la base de datos local.
4.  **Escalación de Casos (`escalar_a_asesor_humano`):** Genera tickets de urgencia en formato de texto dentro de `EP2/tickets/urgentes/` con un ID de formato `ESC-YYYYMMDD_HHMMSS`.

### 3.3 Mecanismo de Memoria Conversacional
Para la memoria a corto plazo, desarrollé una clase llamada `PersistentChatMemory` (`agente/memory.py`). Esta clase almacena el historial de mensajes de la sesión en un archivo JSON local (`history/{session_id}.json`). Cada vez que el usuario envía un mensaje, el historial se carga desde este archivo y se inyecta en el prompt de LangChain, y la respuesta generada por el agente se escribe de vuelta. Esto asegura que si la sesión CLI se interrumpe, el agente puede recuperar el contexto de forma transparente.

### 3.4 Criterios de Derivación y Redirección
El agente monitoriza el flujo de la conversación y activa de forma automática el enrutamiento a un supervisor bajo dos condiciones:
*   **Frustración del cliente:** Si se detectan palabras soeces, quejas repetidas o reclamos fuertes, el agente detiene el proceso de venta, invoca la herramienta de escalación con gravedad **alta**, y se despide de forma empática proporcionando el ticket de seguimiento.
*   **Solicitud fuera de alcance:** Si el usuario pide transferir fondos, cambiar contraseñas o condonar deudas, el agente reconoce que estas acciones exceden sus capacidades de seguridad y ejecuta la escalación con gravedad **media**.

---

## 4. Análisis y Evidencias de los Casos de Prueba

Para verificar que todos los componentes interactúan correctamente, implementé una suite de pruebas automatizadas en `main.py` que valida el comportamiento en tres casos complejos de negocio:

### 4.1 Caso A: Cotización de Crédito de Consumo
*   **Entrada de prueba:** Un cliente solicita cotizar un crédito de consumo de $5.000.000 a 24 cuotas, entregando su nombre y RUT.
*   **Comportamiento:** El agente invoca la calculadora en Python. Retorna los datos exactos (cuota de $258.404 mensuales y costo total de $6.201.700). Luego, el agente recopila estos valores y llama a la herramienta de escritura, generando el documento formal exitosamente en la ruta `EP2/cotizaciones/cotizacion_jose_muñoz_18456789-0_*.txt`.

### 4.2 Caso B: Consulta Normativa y Cumplimiento de la CMF
*   **Entrada de prueba:** El usuario consulta si la tasa ofrecida de 1.8% mensual cumple con la Tasa Máxima Convencional.
*   **Comportamiento:** El agente llama a la herramienta de RAG, recupera las tasas reguladas desde `regulaciones_cmf.txt` en el VectorStore y concluye que la tasa anualizada (23.9% nominal) está muy por debajo del límite máximo establecido (51.0% anual para créditos de consumo inferiores a 200 UF). El agente responde citando la fuente `[Normativa CMF — Comisión para el Mercado Financiero]`.

### 4.3 Caso C: Detección de Frustración y Escalación Autónoma
*   **Entrada de prueba:** Mensaje de un cliente muy enojado reclamando fallas para transferir fondos y exigiendo hablar con un supervisor.
*   **Comportamiento:** El agente detecta que la solicitud está fuera de alcance (transferencia de dinero) y el tono es altamente frustrado. Llama de forma autónoma a la herramienta de escalación con gravedad **alta**, la cual registra el ticket `ESC-20260519_190155` en la carpeta `EP2/tickets/urgentes/` y genera una respuesta de disculpas empática y educada en dialecto chileno.

---

## 5. Conclusiones y Lecciones Aprendidas

1.  **Reducción a cero de alucinaciones matemáticas:** El uso del patrón de herramientas en LangChain para derivar operaciones numéricas a código en Python es una práctica fundamental. Evita que la red neuronal intente hacer matemáticas, logrando exactitud total en cotizaciones reales.
2.  **Cumplimiento Normativo Garantizado:** Al programar las restricciones en el prompt del sistema y combinarlas con RAG, garantizamos que el agente incluya de forma obligatoria las advertencias legales de la CMF, protegiendo a la empresa ante fiscalizaciones regulatorias.
3.  **Seguridad y Empatía en Atención al Cliente:** Identificar de forma autónoma cuándo el bot ya no puede resolver una consulta (acciones fuera de alcance) o cuándo la frustración del cliente es alta permite mantener una experiencia de usuario fluida y libre de callejones sin salida conversacionales.

---

## 6. Referencias Bibliográficas (APA 7)

*   Chase, H. (2022). *LangChain: Libraries for building applications with LLMs through composability*. GitHub. https://github.com/langchain-ai/langchain
*   Comisión para el Mercado Financiero (CMF). (2024). *Normativas sobre tasas máximas convencionales y transparencia en cotizaciones de créditos de consumo*. Gobierno de Chile. https://www.cmfchile.cl
*   OpenAI. (2024). *GPT-4o API and Tool Calling Reference Guide*. OpenAI. https://platform.openai.com/docs
*   Facebook AI Research. (2020). *FAISS: A library for efficient similarity search and clustering of dense vectors*. GitHub. https://github.com/facebookresearch/faiss
