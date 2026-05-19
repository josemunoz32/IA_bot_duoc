# Diagrama de Orquestación y Flujo - AsesorBot Pro

Este documento contiene la representación visual y la explicación de cómo funciona el flujo de trabajo y la toma de decisiones del agente conversacional **AsesorBot Pro** en **FinanChile Asesorías S.A.**

El diseño del agente se basa en el patrón de arquitectura **ReAct (Reasoning and Acting)**, implementado mediante **LangChain** para controlar la memoria a corto plazo, el acceso a la base de conocimientos y el uso de herramientas en base a la entrada del usuario.

## Diagrama de Flujo en Mermaid

El siguiente diagrama muestra el flujo que sigue el agente cada vez que recibe un mensaje del cliente, evaluando si requiere ejecutar herramientas y aplicando las validaciones correspondientes:

```mermaid
graph TD
    %% Estilos de los nodos
    classDef inicio fin fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef proceso fill:#334155,stroke:#94a3b8,stroke-width:1px,color:#fff;
    classDef decision fill:#1e3a8a,stroke:#2563eb,stroke-width:2px,color:#fff;
    classDef tool fill:#065f46,stroke:#059669,stroke-width:2px,color:#fff;
    classDef escalacion fill:#7f1d1d,stroke:#dc2626,stroke-width:2px,color:#fff;
    
    A([Inicio: Entrada del Cliente]) --> B[Cargar Historial Corto Plazo desde history/session_id.json]
    B --> C[Registrar Nuevo Mensaje del Cliente en Historial]
    C --> D[Enviar al Motor LLM GPT-4o con System Prompt & Reglas CMF]
    
    D --> E{¿Requiere Acción / Ejecutar Herramienta?}
    
    %% Ruta sin herramientas
    E -- No --> F[Generar Respuesta Directa]
    F --> G[Citar Fuentes RAG si aplica entre corchetes]
    G --> H[Verificar e Incluir Advertencia CMF de Inversiones]
    H --> I[Guardar Respuesta en history/session_id.json]
    I --> J([Fin: Enviar Respuesta al Cliente])
    
    %% Ruta con herramientas
    E -- Sí --> K{¿Qué Herramienta Ejecutar?}
    
    %% Herramienta 1: Consulta RAG
    K -- Consulta Semántica --> T1[obtener_informacion_financhile]
    T1 --> T1_1[Búsqueda Similitud en FAISS]
    T1_1 --> T1_2[Retornar Fragmentos con Metadata y Fuentes]
    T1_2 --> L[Retroalimentar Contexto al LLM]
    L --> D
    
    %% Herramienta 2: Calculadora Financiera
    K -- Cálculo Matemático --> T2[simular_operacion_financiera]
    T2 --> T2_1[Cálculo de Cuotas con Amortización Francesa o Interés Compuesto]
    T2_1 --> T2_2[Retornar Estructura JSON con Detalle Exacto]
    T2_2 --> L
    
    %% Herramienta 3: Escritura de Documentos
    K -- Escritura Local --> T3[guardar_documento_cliente]
    T3 --> T3_1[Validar Nombre y RUT del Cliente]
    T3_1 --> T3_2[Escribir Archivo en cotizaciones/ o tickets/]
    T3_2 --> T3_3[Retornar Confirmación y Ruta del Archivo]
    T3_3 --> L
    
    %% Herramienta 4: Escalación Humana
    K -- Derivación / Frustración / Operación Compleja --> T4[escalar_a_asesor_humano]
    T4 --> T4_1[Evaluar Nivel de Gravedad: MEDIA o ALTA]
    T4_1 --> T4_2[Escribir Ticket de Emergencia en tickets/urgentes/]
    T4_2 --> T4_3[Retornar ID de Escalación ESC-...]
    T4_3 --> M[Generar Respuesta con Empatía y Derivar Prioritariamente]
    M --> I
    
    %% Control de Bucles
    L --> N{¿Supera max_iterations = 10?}
    N -- Sí --> O[Interrumpir Bucle de Herramientas]
    O --> P[Generar Respuesta Amigable de Contingencia y Soporte]
    P --> I
    N -- No --> D

    %% Aplicación de clases
    class A,J inicio;
    class B,C,L,T1_1,T1_2,T2_1,T2_2,T3_1,T3_2,T3_3,T4_1,T4_2,T4_3,F,G,H,I,O,P proceso;
    class E,K,N decision;
    class T1,T2,T3 tool;
    class T4,M escalacion;
```

---

## Explicación del Flujo y de las Decisiones del Agente

### 1. Gestión de Memoria e Inicio de Turno
Cada vez que el usuario ingresa un mensaje, el sistema lee el archivo JSON correspondiente a su sesión (`history/{session_id}.json`). De esta forma, recuperamos el historial corto plazo para que el agente recuerde variables previas como el nombre o el RUT del cliente. Esto evita pedir los datos una y otra vez.

### 2. Recuperación Semántica (RAG)
Si la consulta del usuario requiere información sobre políticas o productos financieros, el agente decide usar la herramienta `obtener_informacion_financhile`. Esta herramienta busca en la base de datos de vectores en FAISS y retorna los fragmentos de texto más parecidos. Cada fragmento incluye metadatos indicando la fuente de origen (`[Manual de Productos Financieros]`, `[FAQ FinanChile]`, etc.), lo que permite al agente citar explícitamente de dónde sacó la información.

### 3. Cálculos Deterministas en Backend
Para las simulaciones numéricas de cuotas de créditos o proyecciones de ahorro, el agente invoca `simular_operacion_financiera`. Esta herramienta realiza los cálculos matemáticos directamente en Python utilizando fórmulas estándar de ingeniería financiera (como la amortización francesa de cuota fija). De esta forma se eliminan por completo las alucinaciones matemáticas del LLM.

### 4. Automatización Documental
Cuando el cliente aprueba la propuesta de crédito o solicita soporte formal, el agente ejecuta `guardar_documento_cliente`. Esta herramienta exige que se proporcione el nombre y RUT del cliente antes de registrar la cotización o el caso de soporte en un archivo de texto en local (`cotizaciones/` o `tickets/`), simulando la conexión con el CRM de la empresa.

### 5. Derivación Inteligente a Humanos
El agente evalúa de forma constante el tono y el alcance de las consultas del cliente.
- **Por frustración emocional:** Si el cliente utiliza insultos, se expresa de forma muy molesta o exige de forma insistente un supervisor, el agente invoca autónomamente la herramienta `escalar_a_asesor_humano` con gravedad **alta**.
- **Por operaciones fuera de alcance:** Si se solicitan acciones delicadas o transacciones que exceden las políticas de seguridad (como transferir fondos o cambiar contraseñas), el agente inicia la derivación con gravedad **media**.
En ambos casos se crea un ticket de urgencia en `tickets/urgentes/` con un código único `ESC-...` y se le comunica de forma empática al cliente que su caso fue transferido a una persona experta.
