# Propuesta de Caso Organizacional — Evaluación Parcial N°1

## 1. Nombre y Descripción de la Organización

**Nombre:** FinanChile Asesorías S.A.  
**Rubro:** Tecnología Financiera (tecnofinanciera) — Asesoría financiera para personas y PYMES  
**Tamaño:** Mediana empresa (~120 empleados, 3 sucursales en Santiago, Chile)  
**Contexto general:**  
FinanChile Asesorías S.A. es una empresa chilena de tecnología financiera fundada en 2018, regulada por la Comisión para el Mercado Financiero (CMF). Ofrece servicios de asesoría en inversiones, créditos, seguros y planificación financiera personal. Tiene más de 8.000 clientes activos que interactúan con la empresa principalmente por canales digitales (app móvil, web, WhatsApp) y telefónico.

---

## 2. Identificación y Descripción del Problema

**Problema principal:** Saturación del centro de atención al cliente y tiempos de respuesta muy elevados.

El equipo de atención al cliente de FinanChile recibe en promedio **450 consultas diarias**. El 68% son preguntas repetitivas sobre:
- Características y condiciones de productos financieros (tasas, plazos, requisitos)
- Procedimientos para solicitud de créditos y apertura de cuentas
- Dudas regulatorias (qué dice la CMF sobre determinados instrumentos)
- Estado y seguimiento de solicitudes en curso

**Impacto actual:**
- Tiempo promedio de respuesta: **4,2 horas** (objetivo interno: menos de 30 minutos)
- Costo operacional mensual del centro de atención: **$18 millones CLP**
- Tasa de abandono de consultas sin respuesta: **23%**
- ISC (Índice de Satisfacción del Cliente) de atención al cliente: **-12** (negativo)

---

## 3. Objetivos de la Intervención

1. **Reducir el tiempo de respuesta** de 4,2 horas a menos de 2 minutos con un asistente disponible 24/7.
2. **Automatizar el 70%** de las consultas repetitivas para liberar a los asesores y que atiendan casos más complejos.
3. **Mejorar el NPS** de atención al cliente de -12 a +30 en los primeros 6 meses.
4. **Garantizar que las respuestas sean trazables**, indicando siempre de qué documento viene la información.
5. **Bajar los costos operacionales** del centro de atención en un 40%.

---

## 4. Datos Disponibles

### Fuentes Internas (documentos propios de FinanChile)
| Fuente | Tipo | Descripción |
|--------|------|-------------|
| Manual de Productos Financieros | PDF/TXT | Descripción detallada de cada producto: tasas, plazos, comisiones, requisitos |
| Políticas y Procedimientos | PDF/TXT | Flujos de atención, políticas de privacidad, procedimientos de reclamos |
| Base de Conocimiento FAQs | JSON/TXT | Preguntas frecuentes históricas con respuestas validadas por expertos |
| Historial de Tickets | CSV | Consultas pasadas categorizadas (usadas para evaluación del sistema) |

### Fuentes Externas
| Fuente | Tipo | Descripción |
|--------|------|-------------|
| Normativas CMF | PDF/Web | Regulaciones de la Comisión para el Mercado Financiero de Chile |
| Banco Central de Chile | Web API | Tasas de interés vigentes, UF, UTM |
| Diario Oficial Chile | Web | Leyes relevantes al sector financiero |

---

## 5. Restricciones y Requerimientos Particulares

- **Confidencialidad:** Los datos de clientes nunca deben ser incluidos en el contexto enviado al LLM; solo se usan documentos públicos y de conocimiento institucional.
- **Compliance CMF:** Toda respuesta sobre productos financieros debe incluir advertencias legales requeridas por la CMF (ej.: "Las inversiones conllevan riesgo de pérdida de capital").
- **Idioma:** Sistema debe operar exclusivamente en español chileno.
- **Trazabilidad:** Cada respuesta debe indicar el documento fuente del que se extrajo la información (requerimiento de auditoría interna).
- **Latencia:** El tiempo de respuesta no debe superar los 5 segundos para el 95% de las consultas.
- **Escalada humana:** El sistema debe detectar cuando una consulta supera su capacidad y escalar automáticamente a un asesor humano.

---

## 6. Motivación para el Uso de Agentes de IA, LLMs y RAG

### ¿Por qué LLMs?
Los LLMs como GPT-4 pueden entender el lenguaje natural en español, interpretar preguntas ambiguas o incompletas, y responder de forma conversacional. Eso es algo que los sistemas basados en reglas o búsqueda por palabras clave simplemente no logran hacer.

### ¿Por qué RAG y no un LLM genérico?
Un LLM genérico no conoce los productos de FinanChile ni sus tasas actuales, y podría inventar información financiera — lo que en el sector financiero es un riesgo legal serio. RAG resuelve esto porque:
1. **Ancla las respuestas** en documentos oficiales verificados de la empresa
2. **Permite actualizar** el conocimiento sin reentrenar el modelo
3. **Da trazabilidad** citando la fuente de cada respuesta

### ¿Por qué arquitectura de agente?
Un agente IA (vs. una cadena estática) permite:
- Decidir dinámicamente si recuperar de fuentes internas, externas o ambas
- Ejecutar herramientas como consulta de tasas en tiempo real (Banco Central API)
- Detectar y escalar consultas fuera de alcance
- Mantener contexto conversacional entre turnos

---

## 7. Referencias y Anexos

- CMF Chile. (2024). *Norma de Carácter General N°484*. https://www.cmfchile.cl
- Banco Central de Chile. (2024). *API de Indicadores Económicos*. https://si3.bcentral.cl
- Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020. https://arxiv.org/abs/2005.11401
- LangChain. (2024). *RAG Tutorial Documentation*. https://python.langchain.com/docs/tutorials/rag/
