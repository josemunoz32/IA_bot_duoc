# Evaluación Parcial N°2 (EP2) - Agente Autónomo AsesorBot Pro

Este repositorio contiene la entrega de la Evaluación Parcial N°2 (EP2) para el curso de Ingeniería de Soluciones con Inteligencia Artificial. El proyecto consiste en el desarrollo de un Agente Autónomo Funcional (**AsesorBot Pro**) para **FinanChile Asesorías S.A.**

El objetivo del proyecto es evolucionar el sistema RAG básico desarrollado en la EP1 hacia un agente inteligente completo que utiliza memoria conversacional a corto plazo, accede a una base de conocimientos vectorizada, realiza cálculos financieros deterministas mediante código en Python y maneja derivaciones a soporte humano de forma autónoma.

---

## Estructura de Carpetas

El proyecto está organizado de la siguiente manera dentro del directorio `EP2/`:

```text
EP2/
├── .env                  # Configuración de credenciales (Token de GitHub)
├── requirements.txt      # Librerías necesarias para el proyecto (LangChain, FAISS, OpenAI, etc.)
├── main.py               # Archivo ejecutable CLI (modo chat y suite de pruebas)
├── agente/               # Código del agente inteligente
│   ├── __init__.py
│   ├── core.py           # Configuración del Agente (System Prompt, LangChain, ReAct)
│   ├── memory.py         # Control de memoria conversacional guardada en JSON
│   └── tools.py          # Herramientas del agente (RAG, calculadora, guardar cotizaciones/tickets, escalación)
├── data/                 # Archivos de texto con la información de la empresa
├── vectorstore/          # Base de datos vectorial indexada con FAISS
├── history/              # Historial de conversaciones guardado automáticamente
├── cotizaciones/         # Cotizaciones guardadas en formato de texto
├── tickets/              # Tickets de soporte y derivación urgente a asesores
└── entregables/          # Documentación de la evaluación
    ├── README.md                 # Esta guía de uso
    ├── diagrama_orquestacion.md  # Diagrama de flujo Mermaid
    └── informe_tecnico_ep2.md    # Informe formal en formato académico (APA 7)
```

---

## Instalación y Solución del Límite de Ruta de Windows

En entornos Windows, el límite de 260 caracteres en las rutas puede causar que `pip` falle al instalar librerías pesadas en carpetas con nombres largos. Para solucionar esto y garantizar que el código se ejecute sin problemas, configuré un entorno virtual en una ruta corta del sistema:

### 1. Crear el Entorno Virtual en una Ruta Corta
Abre PowerShell o CMD y ejecuta el siguiente comando para crear el entorno en tu carpeta de usuario:
```powershell
python -m venv C:\Users\Usuario\env_ep2
```

### 2. Instalar dependencias
Navega a la carpeta del proyecto `EP2` y ejecuta la instalación utilizando el pip de la ruta corta:
```powershell
C:\Users\Usuario\env_ep2\Scripts\pip.exe install -r requirements.txt
```

---

## Configuración de Variables de Entorno

El archivo `EP2/.env` debe contener tus credenciales para conectarse a GitHub Models. El formato del archivo es:

```ini
GITHUB_TOKEN=tu_token_de_github_aqui
GITHUB_BASE_URL=https://models.inference.ai.azure.com
```

---

## Cómo Ejecutar el Proyecto

El punto de entrada es el archivo `main.py`, el cual tiene dos modos de uso:

### 1. Suite de Pruebas Automatizadas
Para verificar el comportamiento del agente en los tres escenarios clave solicitados en la evaluación, ejecuta el siguiente comando:

```powershell
C:\Users\Usuario\env_ep2\Scripts\python.exe main.py test
```

Este comando simula de forma secuencial tres interacciones:
- **Caso A:** Un cliente (José Muñoz) cotiza un crédito de consumo de $5.000.000 a 24 cuotas. El bot realiza la simulación exacta y escribe un archivo de cotización formal en `EP2/cotizaciones/`.
- **Caso B:** Una consulta regulatoria sobre si la tasa de interés cumple con la Tasa Máxima Convencional de la CMF. El bot busca en la base de datos vectorial y cita la fuente `[Regulaciones CMF]`.
- **Caso C:** Un cliente enojado que exige transferir dinero y hablar con un humano. El bot detecta la frustración y la solicitud fuera de alcance, activa la escalación, genera un ticket de urgencia en `EP2/tickets/urgentes/` y le entrega un código de seguimiento (`ESC-...`).

### 2. Modo Interactivo (Consola de Chat)
Para chatear con el bot libremente en español chileno y probar su comportamiento en vivo, ejecuta:

```powershell
C:\Users\Usuario\env_ep2\Scripts\python.exe main.py
```

Comandos útiles dentro del chat:
- `salir`: Termina la sesión actual.
- `reiniciar`: Borra la memoria persistente del chat actual para empezar una nueva conversación.
- `test`: Ejecuta las pruebas automatizadas directamente desde la consola.
