# Arquitectura de Solución — AsesorBot RAG
## Sistema de Asistencia al Cliente con LLM y RAG — FinanChile Asesorías S.A.

---

## Diagrama de Arquitectura General

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ARQUITECTURA FINANCHILE FINANSBOT v2.0                   ║
║              Sistema RAG + LLM para Atención al Cliente tecnofinanciera              ║
╚══════════════════════════════════════════════════════════════════════════════╝

  CLIENTE                    CAPA DE ACCESO              CAPA DE ORQUESTACIÓN
  ┌───────┐                  ┌──────────────┐            ┌─────────────────────┐
  │  App  │──── HTTPS ──────►│  API Gateway │───────────►│   LangChain Agent   │
  │ Móvil │                  │  (REST API)  │            │   (RetrievalQA)     │
  └───────┘                  └──────────────┘            └────────┬────────────┘
  ┌───────┐                  ┌──────────────┐                     │
  │  Web  │──── HTTPS ──────►│  API Gateway │                     │
  │Browser│                  │  (REST API)  │            ┌────────▼────────────┐
  └───────┘                  └──────────────┘            │   RAG PIPELINE      │
  ┌──────────┐               ┌──────────────┐            │                     │
  │WhatsApp  │──── API ──────►│  Webhook     │            │  1. Embed Query     │
  │Chatbot   │               │  Handler     │            │  2. Vector Search   │
  └──────────┘               └──────────────┘            │  3. Context Build   │
                                                          │  4. LLM Generate   │
                                                          └────────┬────────────┘
                                                                   │
              ┌────────────────────────────────────────────────────┘
              │
   ┌──────────▼──────────────────────────────────────────────────────┐
   │                   CAPA DE RECUPERACIÓN                          │
   │                                                                  │
   │  ┌──────────────────┐    ┌──────────────────────────────────┐  │
   │  │  VECTOR STORE    │    │      FUENTES DE DATOS            │  │
   │  │    (FAISS)       │◄───┤                                  │  │
   │  │                  │    │  INTERNAS:                       │  │
   │  │  - Embeddings    │    │  📄 Manual Productos.txt         │  │
   │  │    1536 dims     │    │  📄 Políticas Empresa.txt        │  │
   │  │  - ~200+ chunks  │    │  📄 FAQ FinanChile.txt           │  │
   │  │  - Similarity    │    │                                  │  │
   │  │    Search        │    │  EXTERNAS:                       │  │
   │  │                  │    │  🌐 Normativa CMF (regulaciones) │  │
   │  └──────────────────┘    │  🌐 Banco Central (indicadores)  │  │
   │                          └──────────────────────────────────┘  │
   └──────────────────────────────────────────────────────────────────┘
              │
   ┌──────────▼──────────────────────────────────────────────────────┐
   │                   CAPA DE GENERACIÓN                             │
   │                                                                  │
   │  ┌──────────────────────────────────────────────────────────┐  │
   │  │   GPT-4o (Azure / GitHub Models)                         │  │
   │  │                                                          │  │
   │  │   Input:  System Prompt Maestro                          │  │
   │  │         + Context (chunks recuperados)                   │  │
   │  │         + User Query                                     │  │
   │  │                                                          │  │
   │  │   Output: Respuesta en español                           │  │
   │  │          + Fuente citada                                 │  │
   │  │          + Advertencias CMF (si aplica)                  │  │
   │  │          + Protocolo de escalada (si aplica)             │  │
   │  └──────────────────────────────────────────────────────────┘  │
   └──────────────────────────────────────────────────────────────────┘
              │
   ┌──────────▼──────────────────────────────────────────────────────┐
   │                   CAPA DE SEGURIDAD Y CUMPLIMIENTO               │
   │                                                                  │
   │  ✅ Filtro PII: Nunca procesa claves, contraseñas ni datos      │
   │                 personales sensibles del cliente                 │
   │  ✅ Advertencias CMF: Incluidas automáticamente en respuestas   │
   │                       sobre inversiones                          │
   │  ✅ Trazabilidad: Log de cada consulta + chunks usados          │
   │  ✅ Escalada: Derivación a asesor humano cuando corresponde     │
   │  ✅ Rate Limiting: Máx. 100 consultas/minuto por usuario        │
   └──────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos Detallado

```
FASE A — INDEXACIÓN (se ejecuta una vez al actualizar documentos)
══════════════════════════════════════════════════════════════

  Documentos TXT/PDF
       │
       ▼
  [RecursiveCharacterTextSplitter]
       │ chunk_size=500, chunk_overlap=100
       ▼
  Chunks de texto (c. 200)
       │
       ▼
  [text-embedding-3-small]
       │ 1536 dimensiones por chunk
       ▼
  Vectores de embeddings
       │
       ▼
  [FAISS.from_documents()]
       │ Índice FlatL2
       ▼
  Vector Store (persiste en disco: ./financhile_vectorstore/)


FASE B — CONSULTA (se ejecuta en tiempo real para cada pregunta)
══════════════════════════════════════════════════════════════

  Pregunta del usuario (texto natural)
       │
       ▼
  [text-embedding-3-small]
       │ Convierte pregunta a vector de 1536 dims
       ▼
  Vector de consulta
       │
       ▼
  [FAISS similarity_search(k=4)]
       │ Busca los 4 chunks más similares
       ▼
  Chunks relevantes (contexto)
       │
       ├── + Pregunta original
       ├── + System Prompt Maestro (restricciones CMF, identidad AsesorBot)
       │
       ▼
  [Prompt Template combinado]
       │
       ▼
  [GPT-4o (T=0.1)]
       │
       ▼
  Respuesta final con:
  - Información factual de los documentos
  - Fuentes citadas ([Manual], [CMF], etc.)
  - Advertencias legales cuando aplica
  - Protocolo de escalada cuando aplica
```

---

## Componentes Clave e Integración

| Componente | Tecnología | Rol | Justificación |
|-----------|-----------|-----|---------------|
| **LLM** | GPT-4o (T=0.1) | Generación de respuestas naturales | Mayor precisión factual y comprensión del español chileno |
| **Embeddings** | text-embedding-3-small | Representación semántica vectorial | Modelo costo-eficiente con alta calidad semántica |
| **Vector Store** | FAISS | Búsqueda de similitud eficiente | Open-source, sin costo de uso, rápido en memoria |
| **Orquestación** | LangChain RetrievalQA | Integración RAG completa | Framework maduro con amplio soporte |
| **Chunking** | RecursiveCharacterTextSplitter | Fragmentación óptima de documentos | Preserva estructura semántica del texto financiero |
| **API** | OpenAI-compatible (Azure) | Acceso al modelo | Compatible con GitHub Models y Azure OpenAI |
| **Seguridad** | Filtros de prompt | Prevención de fuga de datos | Cumplimiento con Ley 19.628 y políticas CMF |

---

## Decisiones de Arquitectura Justificadas

### 1. FAISS vs Pinecone/Chroma
**Decisión:** FAISS (local, in-memory)  
**Justificación:** Para el MVP y validación del caso, FAISS no tiene costos de operación, no requiere conexión externa y permite persistir el índice en disco. En producción, se migraría a un servicio gestionado (Pinecone o Azure AI Search) para escalar.

### 2. chain_type="stuff" vs "map_reduce"
**Decisión:** `stuff` (todos los chunks en un solo contexto)  
**Justificación:** Con k=4 chunks de 500 chars cada uno (~2.000 tokens de contexto), cabe perfectamente en la ventana de contexto de GPT-4o (128K tokens). El `stuff` es más simple y preciso para consultas donde el contexto es pequeño.

### 3. k=4 en el retriever
**Decisión:** Recuperar 4 chunks  
**Justificación:** Pruebas empíricas mostraron que k=4 captura suficiente contexto sin introducir ruido. Con k=2 se perdía información relevante; con k=8 el modelo ignoraba chunks irrelevantes generando respuestas menos enfocadas.

### 4. Temperatura 0.1
**Decisión:** T=0.1 (casi determinístico)  
**Justificación:** En dominio financiero regulado, la consistencia y precisión factual son más importantes que la creatividad. Una temperatura alta podría generar tasas o condiciones inventadas, con potencial riesgo legal para FinanChile.

### 5. Separación fuentes internas/externas
**Decisión:** Metadata diferenciada por `source_type`  
**Justificación:** Permite auditar qué tipo de fuente respaldó cada respuesta. En caso de discrepancia entre una política interna y una regulación CMF, la arquitectura puede priorizar la fuente correcta.
