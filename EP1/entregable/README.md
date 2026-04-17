# AsesorBot — Sistema RAG para Atención al Cliente FinanChile
## Evaluación Parcial N°1 | ISY0101 — Ingeniería de Soluciones con IA

**Alumno:** José Muñoz

> **Caso organizacional:** FinanChile Asesorías S.A. — Asistente IA para atención al cliente en empresa tecnofinanciera chilena regulada por la CMF.

---

## Descripción del Proyecto

**AsesorBot** es un asistente de IA conversacional que construimos para resolver un problema real: los clientes de FinanChile esperaban horas por una respuesta a consultas que en su mayoría eran repetitivas. El sistema usa un pipeline **RAG (Retrieval-Augmented Generation)** para responder preguntas sobre productos financieros, regulaciones y procedimientos usando como base los documentos oficiales de la empresa.

### Problema que resuelve
- Tiempo promedio de respuesta actual: **4,2 horas** → Objetivo: **<2 minutos**
- 68% de consultas son repetitivas y pueden ser automatizadas
- El sistema RAG garantiza que las respuestas estén **ancladas en documentos oficiales** verificados, eliminando el riesgo de "alucinaciones" con información financiera incorrecta

### Tecnologías utilizadas
- **LLM:** GPT-4o (via GitHub Models / Azure OpenAI)
- **Framework:** LangChain (RetrievalQA)
- **Embeddings:** text-embedding-3-small
- **Vector Store:** FAISS
- **Lenguaje:** Python 3.11+

---

## Estructura del Proyecto

```
EP1/
├── README.md                          # Este archivo
├── caso_organizacional.md             # Propuesta del caso (IE1)
├── arquitectura_diagrama.md           # Diagrama de arquitectura (IE5, IE6)
├── informe_tecnico.md                 # Informe técnico completo (IE7, IE8, IE9)
│
├── 1-prompts-optimizados.ipynb        # Técnicas de prompting (IE2)
├── 2-rag-pipeline.ipynb               # Pipeline RAG + evaluación coherencia (IE3, IE4)
│
└── data/                              # Base documental (knowledge base)
    ├── manual_productos_financieros.txt   # FUENTE INTERNA — Manual de productos
    ├── politicas_empresa.txt              # FUENTE INTERNA — Políticas y procedimientos
    ├── faq_financhile.txt                 # FUENTE INTERNA — Preguntas frecuentes
    └── regulaciones_cmf.txt              # FUENTE EXTERNA — Normativa CMF + indicadores BC
```

---

## Requisitos del Sistema

- Python **3.11** o superior
- pip (gestor de paquetes)
- Cuenta de GitHub con acceso a **GitHub Models** (gratuito)
- Conexión a internet (para llamadas a la API)

---

## Instalación y Configuración

### Paso 1: Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd EP1
```

### Paso 2: Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
pip install openai langchain langchain-openai langchain-community faiss-cpu python-dotenv requests jupyter
```

O usando el archivo de requerimientos:

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno

Crea un archivo `.env` en la carpeta `EP1/` con el siguiente contenido:

```env
GITHUB_TOKEN=tu_token_de_github_aqui
GITHUB_BASE_URL=https://models.inference.ai.azure.com
```

**¿Cómo obtener tu GitHub Token?**
1. Ve a https://github.com/settings/tokens
2. Genera un token clásico con permisos de lectura
3. Copia el token y pégalo en el archivo `.env`

> ⚠️ **Nunca subas el archivo `.env` a GitHub.** Está incluido en `.gitignore`.

### Paso 5: Cargar variables de entorno

**Opción A — Usando python-dotenv (en el notebook):**  
El primer bloque de configuración de cada notebook carga automáticamente el `.env`.

**Opción B — Variables de entorno del sistema:**

```bash
# Windows (PowerShell)
$env:GITHUB_TOKEN="tu_token_aqui"
$env:GITHUB_BASE_URL="https://models.inference.ai.azure.com"

# macOS / Linux
export GITHUB_TOKEN="tu_token_aqui"
export GITHUB_BASE_URL="https://models.inference.ai.azure.com"
```

---

## Ejecución de los Notebooks

### Iniciar Jupyter

```bash
jupyter notebook
```

Se abrirá el navegador en `http://localhost:8888`. Navega hasta la carpeta `EP1/`.

### Orden de ejecución recomendado

| Notebook | Descripción | Tiempo estimado |
|----------|-------------|-----------------|
| `1-prompts-optimizados.ipynb` | Diseño y comparación de técnicas de prompting | ~5 min |
| `2-rag-pipeline.ipynb` | Pipeline RAG completo + evaluación de coherencia | ~10 min |

> 💡 **Tip:** Ejecuta las celdas en orden secuencial con `Shift + Enter`. El notebook `2-rag-pipeline.ipynb` puede tomar más tiempo en la celda de construcción del vector store ya que debe generar embeddings para todos los chunks.

---

## Verificación del Sistema

Tras ejecutar `2-rag-pipeline.ipynb` completamente, el sistema debe:

1. ✅ Cargar los 4 documentos de la knowledge base (3 internos + 1 externo)
2. ✅ Generar ~200 chunks de texto
3. ✅ Construir el índice FAISS y guardarlo en `./financhile_vectorstore/`
4. ✅ Responder consultas de prueba con fuentes citadas
5. ✅ Mostrar cobertura conceptual >80% en la evaluación de coherencia

---

## Ejemplos de Consultas al Sistema

Una vez ejecutado el pipeline, puedes probar consultas directamente desde el notebook:

```python
consultar_financhile("¿Cuáles son los requisitos para pedir un crédito de consumo?")
consultar_financhile("¿Cuánto rinde el Fondo Conservador?")
consultar_financhile("Quiero presentar un reclamo, ¿cómo lo hago?")
consultar_financhile("¿La tasa del crédito cumple con los límites de la CMF?")
```

---

## Dependencias Principales

```
openai>=1.30.0
langchain>=0.2.0
langchain-openai>=0.1.0
langchain-community>=0.2.0
faiss-cpu>=1.8.0
python-dotenv>=1.0.0
requests>=2.31.0
jupyter>=1.0.0
ipykernel>=6.0.0
```

---

## Herramientas de IA Utilizadas (Declaración Ética)

En cumplimiento con las indicaciones del curso:

| Herramienta | Uso | Validado por el equipo |
|-------------|-----|------------------------|
| GitHub Copilot | Autocompletar fragmentos de código Python | ✅ Sí |
| GPT-4o | Apoyo en redacción de documentación técnica | ✅ Sí |

Todas las ideas, análisis de casos, decisiones de diseño arquitectónico y justificaciones técnicas son propias del equipo. El código fue revisado y validado en su totalidad antes de la entrega.

---

## Autores

- **[Nombre Estudiante 1]** — [Rol en el proyecto]
- **[Nombre Estudiante 2]** — [Rol en el proyecto]

Curso: ISY0101 — Ingeniería de Soluciones con IA  
Institución: DuocUC  
Semestre: 1-2025

---

## Referencias

- Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020. https://arxiv.org/abs/2005.11401
- LangChain. (2024). *RAG Tutorial*. https://python.langchain.com/docs/tutorials/rag/
- CMF Chile. (2024). *Normativa para Empresas tecnofinanciera*. https://www.cmfchile.cl
- OpenAI. (2024). *text-embedding-3-small documentation*. https://platform.openai.com/docs/guides/embeddings
