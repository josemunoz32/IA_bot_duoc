# Informe Técnico — Evaluación Parcial N°1
## Diseño de Solución con LLM y RAG
### ISY0101 — Ingeniería de Soluciones con Inteligencia Artificial

**Institución:** DuocUC  
**Asignatura:** ISY0101 — Ingeniería de Soluciones con IA  
**Alumno:** José Muñoz  
**Fecha:** Abril 2026

---

## Resumen Ejecutivo

En este informe describimos el proceso de diseño e implementación de **AsesorBot**, un asistente de IA que desarrollamos para resolver un problema real de atención al cliente en **FinanChile Asesorías S.A.**, empresa tecnofinanciera chilena regulada por la CMF. El problema era concreto: los clientes esperaban en promedio 4,2 horas por una respuesta y casi un 23% simplemente abandonaba la consulta. Nuestra propuesta fue construir un sistema RAG que combine documentos internos de la empresa (manuales, políticas, FAQ) con fuentes externas (normativa CMF, indicadores del Banco Central), de modo que las respuestas siempre estén respaldadas por información oficial y trazable. Al probarlo, logramos una cobertura conceptual sobre el 80% y tiempos de respuesta bajo los 5 segundos.

---

## A. Análisis del Caso Organizacional (IE1)

### A.1 Descripción de la Organización

FinanChile Asesorías S.A. es una empresa de tecnología financiera (tecnofinanciera) fundada en 2018, con sede en Santiago de Chile. Opera bajo regulación de la Comisión para el Mercado Financiero (CMF, registro N°1247) y cuenta con aproximadamente 120 empleados distribuidos en tres sucursales. Su cartera activa supera los 8.000 clientes, quienes acceden a servicios de asesoría en inversiones, créditos, seguros y planificación financiera personal principalmente a través de canales digitales.

### A.2 Identificación del Problema

El análisis del proceso de atención al cliente reveló los siguientes indicadores críticos:

| KPI Actual | Valor Actual | Objetivo |
|-----------|--------------|---------|
| Tiempo promedio de respuesta | 4,2 horas | < 2 minutos |
| Tasa de abandono de consultas | 23% | < 5% |
| Consultas automatizables (repetitivas) | 68% | Automatizar 70% |
| Costo mensual centro de atención | $18M CLP | Reducir 40% |
| NPS de atención | -12 | +30 |

La causa raíz identificada es la **ausencia de un sistema de atención automatizado** capaz de manejar consultas de conocimiento sobre productos y regulaciones en tiempo real, con la precisión y el cumplimiento normativo que exige el sector financiero.

### A.2.1 Requerimientos Específicos

| ID | Requerimiento | Prioridad |
|----|--------------|-----------|
| REQ-01 | Respuestas basadas exclusivamente en documentación oficial verificada | Alta |
| REQ-02 | Trazabilidad: cada respuesta debe citar su fuente documental | Alta |
| REQ-03 | Advertencias legales CMF automáticas en respuestas sobre inversiones | Alta |
| REQ-04 | Protocolo de escalada a asesor humano en casos complejos | Alta |
| REQ-05 | Latencia de respuesta < 5 segundos para el 95% de las consultas | Media |
| REQ-06 | Soporte de fuentes externas (regulaciones actualizadas, tasas de mercado) | Media |
| REQ-07 | No procesar datos sensibles del cliente (contraseñas, números de tarjeta) | Alta |

### A.3 Justificación del Uso de IA

Antes de decidir usar LLMs, consideramos la opción de un chatbot clásico basado en reglas. La descartamos rápidamente por tres razones:
1. Los clientes no preguntan siempre igual — la variabilidad del lenguaje natural hace imposible cubrir todos los casos con reglas fijas
2. Las tasas y regulaciones cambian constantemente, lo que implicaría reprogramar el bot cada vez
3. Hay consultas que mezclan varios temas a la vez (por ejemplo: "¿la tasa que ofrecen está dentro de lo que permite la CMF?") que un chatbot clásico simplemente no puede manejar

Con LLM + RAG, en cambio, el sistema entiende el lenguaje natural del cliente, busca la información relevante en los documentos y genera una respuesta contextualizada — sin necesidad de reentrenar el modelo cuando algo cambia.

---

## B. Formulación de Prompts (IE2)

### B.1 Estrategia de Prompt Engineering

Probamos cuatro técnicas de prompting distintas, que están documentadas con detalle en el notebook `1-prompts-optimizados.ipynb`:

| Técnica | Caso de Uso | Calidad Resultante |
|---------|-------------|-------------------|
| Zero-Shot | Consultas simples sobre productos | Media-Alta |
| Few-Shot | Comparaciones entre productos | Alta |
| Chain-of-Thought | Análisis financiero con cálculos | Muy Alta |
| **System Prompt Maestro** | **Integración completa (producción)** | **Máxima** |

### B.2 System Prompt Maestro — Decisiones de Diseño

El system prompt maestro integra las siguientes secciones críticas:

**1. Identidad y contexto regulatorio:**
```
"Eres AsesorBot, el asistente virtual oficial de FinanChile Asesorías S.A., 
empresa regulada por la CMF de Chile (registro N°1247)."
```
*Justificación:* Proporciona contexto institucional explícito para que el modelo comprenda el dominio y las restricciones aplicables.

**2. Restricciones legales integradas:**
```
"ADVERTENCIA CMF: Las inversiones en fondos mutuos conllevan riesgo de 
pérdida de capital. Los rendimientos históricos no garantizan rendimientos futuros."
```
*Justificación:* La NCG N°484 de la CMF obliga a incluir advertencias de riesgo en toda comunicación sobre instrumentos de inversión. Integrarlas en el prompt garantiza cumplimiento automático.

**3. Protocolo de escalada:**
```
"Para disputas legales, montos >$100M o situaciones de fraude activo, 
deriva al 600-FINANS."
```
*Justificación:* Limita el ámbito de acción del modelo, reduciendo el riesgo de respuestas incorrectas en casos complejos.

**4. Temperatura 0.1:**
*Justificación:* En dominio financiero regulado, la consistencia factual supera en importancia a la creatividad. Una temperatura alta podría generar tasas o condiciones incorrectas con implicaciones legales para la empresa.

### B.3 Comparativa de Resultados

Para la consulta "¿Puedo pedir un crédito con 3 meses de antigüedad laboral?":

| Configuración | Precisión | Cumplimiento Legal | Utilidad |
|--------------|-----------|-------------------|---------|
| Sin prompt engineering | Baja (inventó requisitos) | No | 2/10 |
| Zero-Shot básico | Media (respuesta genérica) | Parcial | 6/10 |
| System Prompt Maestro | Alta (requisito exacto: 6 meses) | Completo | 10/10 |

---

## C. Diseño e Implementación del Pipeline RAG (IE3 e IE4)

### C.1 Arquitectura del Pipeline

Implementamos el pipeline RAG usando LangChain, dividido en dos fases:

**Fase de Indexación** (ejecución única al actualizar documentos):

```
Documentos (TXT/PDF) → Chunking → Embeddings → FAISS Index
```

**Fase de Consulta** (ejecución en tiempo real):

```
Query → Embed Query → Similarity Search → Contexto → GPT-4o → Respuesta
```

### C.2 Fuentes de Datos Internas

| Documento | Chunks generados | Tipo de conocimiento |
|-----------|-----------------|---------------------|
| manual_productos_financieros.txt | ~85 chunks | Tasas, condiciones, requisitos de productos |
| politicas_empresa.txt | ~70 chunks | Procedimientos, políticas, horarios |
| faq_financhile.txt | ~45 chunks | Respuestas validadas a preguntas frecuentes |

Estos documentos tienen todo el conocimiento específico de FinanChile: tasas, procedimientos, políticas. Es información que un LLM genérico simplemente no tiene, y es lo que hace que el sistema sea útil en la práctica.

### C.3 Fuentes de Datos Externas

| Fuente | Chunks generados | Tipo de conocimiento |
|--------|-----------------|---------------------|
| regulaciones_cmf.txt | ~60 chunks | Normativa CMF, derechos del consumidor, TMC |
| Indicadores Banco Central | ~15 chunks | UF, UTM, TPM, tasas de mercado |

Las fuentes externas sirven para contextualizar las respuestas dentro del marco regulatorio. Por ejemplo, con estas fuentes el sistema puede responder si una tasa ofrecida por FinanChile está dentro de los límites legales que establece la CMF, o cómo se compara con el mercado.

### C.4 Parámetros de Chunking y Justificación

```python
RecursiveCharacterTextSplitter(
    chunk_size=500,    # Equilibrio entre granularidad y contexto suficiente
    chunk_overlap=100  # 20% de solapamiento preserva contexto entre límites de chunks
)
```

**Justificación del chunk_size=500:** Los documentos financieros contienen secciones bien definidas (un producto, una política). Chunks de 500 chars capturan generalmente una sección completa sin exceder el contexto. Chunks más grandes incluirían información de productos distintos mezclados, reduciendo la precisión del retriever.

**Justificación del overlap=100 (20%):** Las condiciones de un producto financiero frecuentemente cruzan el límite de una sección. El solapamiento del 20% garantiza que, por ejemplo, los requisitos de un crédito (que pueden continuar en el siguiente chunk) sean recuperados correctamente.

### C.5 Evaluación de Coherencia (IE4)

Para verificar que las respuestas fueran coherentes con los documentos fuente, diseñamos un protocolo simple de palabras clave: si la respuesta del sistema incluye los conceptos clave esperados, consideramos que el RAG está funcionando bien.

| Consulta de prueba | Keywords esperadas | Cobertura |
|-------------------|-------------------|-----------|
| "¿Tasa DAP 90 días?" | ["5,8%", "90", "anual"] | 100% |
| "¿Mínimo Fondo Conservador?" | ["100.000", "conservador"] | 100% |
| "¿Días hábiles para reclamo?" | ["10", "días hábiles", "reclamo"] | 100% |
| "¿TMC crédito consumo CMF?" | ["51", "cmf", "tasa máxima"] | 100% |

**Cobertura conceptual promedio: 100%** — en todos los casos de prueba, el sistema recuperó y reprodujo correctamente los datos desde los documentos.

**Trazabilidad:** todas las respuestas incluyen la fuente entre corchetes (ej.: "[Manual de Productos Financieros]"), lo que permite auditar de dónde viene cada información.

---

## D. Arquitectura de la Solución (IE5 e IE6)

### D.1 Visión General

La arquitectura de AsesorBot se organiza en cuatro capas bien diferenciadas:

```
┌─────────────────────────────────────────────────────────────┐
│ CAPA 1: ACCESO — Canales: App, Web, WhatsApp                │
├─────────────────────────────────────────────────────────────┤
│ CAPA 2: ORQUESTACIÓN — LangChain RetrievalQA Agent          │
├─────────────────────────────────────────────────────────────┤
│ CAPA 3: RECUPERACIÓN — FAISS Vector Store + Retriever       │
│         (Fuentes internas + externas indexadas)             │
├─────────────────────────────────────────────────────────────┤
│ CAPA 4: GENERACIÓN — GPT-4o + System Prompt Maestro         │
└─────────────────────────────────────────────────────────────┘
```

El diagrama completo con ASCII art y descripciones detalladas se encuentra en [arquitectura_diagrama.md](./arquitectura_diagrama.md).

### D.2 Módulos Principales

**Módulo de Recuperación:**
- Entrada: Query en lenguaje natural
- Proceso: Embedding de la query → Búsqueda por similitud coseno en FAISS (k=4)
- Salida: Top-4 chunks más relevantes con metadata de fuente

**Módulo de Procesamiento:**
- Entrada: Query + chunks recuperados
- Proceso: Construcción del prompt RAG (template + contexto + restricciones legales)
- Salida: Prompt enriquecido listo para el LLM

**Módulo de Generación:**
- Entrada: Prompt enriquecido
- Proceso: Inferencia GPT-4o (T=0.1, max_tokens=800)
- Salida: Respuesta en español con fuente citada y advertencias legales

### D.3 Flujo de Datos con Trazabilidad

```
Usuario: "¿Cuánto me rinde el Fondo Conservador?"
    │
    ▼ Embedding: [0.023, -0.156, ..., 0.089] (1536 dims)
    │
    ▼ FAISS Search: Recupera chunks sobre Fondo Conservador
      - Chunk de manual_productos (0.91 similarity): "...6,8% anual histórico..."
      - Chunk de faq (0.87 similarity): "...rentabilidad 6,8%..."
    │
    ▼ Prompt RAG: Sistema + Contexto + Pregunta
    │
    ▼ GPT-4o: Genera respuesta
    │
AsesorBot: "El Fondo Conservador ha tenido una rentabilidad histórica de 6,8% anual.
           ADVERTENCIA CMF: Las inversiones conllevan riesgo de pérdida de capital.
           [Fuente: Manual de Productos Financieros]"
```

---

## E. Documentación Técnica (IE7 e IE8)

### E.1 Justificación de Decisiones de Diseño

| Decisión | Alternativas Evaluadas | Decisión Final | Justificación |
|----------|----------------------|----------------|---------------|
| LLM | GPT-3.5-turbo, Claude, Gemini | GPT-4o | Mayor comprensión del español y razonamiento financiero |
| Vector DB | Pinecone, Chroma, Weaviate | FAISS | Sin costo operacional, suficiente para el volumen del MVP |
| chain_type | map_reduce, refine, map_rerank | stuff | Contexto pequeño (k=4 × 500 chars); menor latencia |
| chunk_size | 200, 350, 500, 750 | 500 | Balance empírico entre granularidad y cobertura contextual |
| k retriever | 2, 4, 6, 8 | 4 | k=2 pierde contexto; k>4 introduce ruido en respuestas |
| Temperatura | 0.0, 0.1, 0.3, 0.7 | 0.1 | Mínimo ruido estocástico manteniendo fluidez natural |
| Embeddings | text-embedding-ada-002, text-embedding-3-large | text-embedding-3-small | Mayor calidad que ada-002; menor costo que 3-large |

### E.2 Matriz de Trazabilidad Requerimiento-Implementación

| Requerimiento | Componente Implementado | Evidencia en Código |
|--------------|------------------------|---------------------|
| REQ-01: Respuestas en documentación oficial | RAG con FAISS | `return_source_documents=True` |
| REQ-02: Trazabilidad con fuente | Metadata en chunks | `doc.metadata.get('source')` |
| REQ-03: Advertencias CMF automáticas | System Prompt Maestro | Sección "RESTRICCIONES LEGALES" |
| REQ-04: Protocolo de escalada | System Prompt Maestro | Sección "ESCALADA AUTOMÁTICA" |
| REQ-05: Latencia < 5s | FAISS in-memory, T=0.1 | Pruebas de tiempo documentadas |
| REQ-06: Fuentes externas | Carga de regulaciones CMF + BC | `external_docs` en notebook 2 |
| REQ-07: No procesar datos sensibles | Filtro en System Prompt | Restricción explícita en prompt |

### E.3 Limitaciones Conocidas del Sistema

| Limitación | Descripción | Mitigación propuesta |
|-----------|-------------|---------------------|
| Hallucination residual | El modelo puede inferir datos no presentes en el contexto | Temperatura 0.1 + instrucción explícita de "no inventar" |
| Contexto estático | Los documentos no se actualizan en tiempo real | Pipeline de actualización periódica (cron job mensual) |
| Español estándar | El modelo no siempre usa modismos chilenos | Fine-tuning o ejemplos few-shot adicionales |
| FAISS in-memory | No persiste en entorno serverless | Migrar a FAISS persistente o Pinecone en producción |
| Escalabilidad | FAISS no soporta alta concurrencia | Migrar a servicio gestionado (Azure AI Search) para >1000 QPS |

### E.4 Métricas de Evaluación del Sistema

| Métrica | Valor Medido | Umbral Objetivo |
|---------|-------------|-----------------|
| Cobertura conceptual (evaluación keywords) | ~100% | >80% |
| Presencia de advertencias CMF en respuestas sobre inversión | 100% | 100% |
| Respuestas con fuente citada | 100% | 100% |
| Consultas con escalada correcta (fuera de scope) | 100% | 100% |
| Tiempo de respuesta promedio (notebook local) | ~3-4 segundos | <5 segundos |

---

## F. Conclusiones

### F.1 Reflexión Técnica del Equipo

Trabajando en este proyecto aprendimos varias cosas que no estaban del todo claras al principio:

1. **El prompt engineering importa más de lo que pensábamos**: Al comparar las respuestas con y sin un system prompt bien diseñado, la diferencia fue enorme. No es solo estética — un prompt mal construido en un contexto financiero regulado puede dar información incorrecta con consecuencias reales.

2. **RAG resuelve el problema de las alucinaciones en dominios específicos**: El modelo base no sabe las tasas de FinanChile ni sus procedimientos internos. Sin RAG, inventaría datos. Con RAG, solo puede responder con lo que está en los documentos — eso es justamente lo que necesita una empresa del sector financiero.

3. **Citar la fuente no es solo un requisito formal**: Al principio lo veíamos como una exigencia de la rúbrica. Después entendimos que es lo que hace confiable al sistema — el cliente puede verificar de dónde viene la información.

4. **Los parámetros chunk_size y k afectan directamente la calidad**: Ajustarlos fue la parte que tomó más tiempo. Con chunks muy pequeños, la respuesta perdía contexto. Con k muy alto, se recuperaba información de otros productos que contaminaba la respuesta.

### F.2 Reflexión Individual — José Muñoz

Ya venía con experiencia usando modelos de lenguaje, así que la parte de conectar la API y armar los prompts no fue lo más difícil. Lo que más me costó fue el pipeline RAG: entender por qué los chunks importan tanto y cómo un parámetro mal ajustado hace que el modelo recupere contexto de otro producto y contamine la respuesta. Eso lo aprendí a prueba y error.

Lo más valioso fue aplicarlo en un caso real con restricciones legales. No es lo mismo hacer un chatbot de prueba que diseñar uno donde cada respuesta tiene implicancias regulatorias. Eso me obligó a pensar en el sistema completo, no solo en si el modelo respondía bien.



---

## G. Referencias (Norma APA 7ª edición)

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W. T., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*, *33*, 9459–9474. https://arxiv.org/abs/2005.11401

LangChain. (2024). *RAG tutorial*. LangChain Documentation. https://python.langchain.com/docs/tutorials/rag/

Comisión para el Mercado Financiero. (2024). *Norma de carácter general N°484*. CMF Chile. https://www.cmfchile.cl

OpenAI. (2024). *Text embedding models: text-embedding-3-small*. OpenAI Platform. https://platform.openai.com/docs/guides/embeddings

Banco Central de Chile. (2025). *Indicadores económicos y financieros*. Banco Central de Chile. https://www.bcentral.cl

Facebook AI Research. (2024). *FAISS: A library for efficient similarity search*. GitHub. https://github.com/facebookresearch/faiss

Ministerio de Hacienda de Chile. (2023). *Ley N°21.521: Modernización de la legislación financiera (Ley tecnofinancieras)*. Diario Oficial de Chile. https://www.bcn.cl/leychile/navegar?idNorma=1190636

---

## Declaración de Uso de IA

De acuerdo a las directrices de DuocUC (https://bibliotecas.duoc.cl/ia):

| Herramienta IA | Uso específico | Validación del equipo |
|---------------|---------------|----------------------|
| GitHub Copilot | Apoyo con autocompletado en código Python | ✅ Todo el código fue revisado y probado por el equipo |

Los análisis, justificaciones técnicas, reflexiones individuales y el informe en general fueron redactados por el equipo.
