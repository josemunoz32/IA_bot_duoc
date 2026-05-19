import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from agente.memory import PersistentChatMemory
from agente.tools import (
    obtener_informacion_financhile,
    simular_operacion_financiera,
    guardar_documento_cliente,
    escalar_a_asesor_humano
)

# Cargar variables de entorno
load_dotenv()

class FinanChileAgent:
    """
    Clase principal que representa y orquesta al Agente Funcional de FinanChile (AsesorBot Pro).
    Integra el modelo LLM, la memoria persistente a corto plazo y el conjunto de herramientas
    autónomas (Consulta RAG, Calculadora Financiera, Escritura de propuestas/tickets y Escalación).
    """
    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        # Inicializar memoria persistente para la sesión
        self.memory = PersistentChatMemory(session_id=session_id)
        
        # Configurar cliente LLM utilizando las variables de entorno de GitHub Models
        api_base = os.getenv("GITHUB_BASE_URL", "https://models.inference.ai.azure.com")
        token = os.getenv("GITHUB_TOKEN", "")
        
        # Definir el modelo GPT-4o a utilizar
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            openai_api_base=api_base,
            openai_api_key=token
        )
        
        # Definir la lista de herramientas autónomas
        self.tools = [
            obtener_informacion_financhile,
            simular_operacion_financiera,
            guardar_documento_cliente,
            escalar_a_asesor_humano
        ]
        
        # Construir el AgentExecutor
        self.agent_executor = self._build_agent_executor()

    def _build_agent_executor(self) -> AgentExecutor:
        """Construye e inicializa el agente de herramientas y su ejecutor."""
        # Mensaje del sistema con instrucciones detalladas, reglas del negocio y compliance
        system_prompt = (
            "Eres AsesorBot Pro, el asistente virtual oficial de FinanChile Asesorías S.A., "
            "empresa de asesorías financieras para personas y PYMES regulada por la CMF (registro N°1247).\n\n"
            
            "REGLAS CRÍTICAS DE COMPORTAMIENTO:\n"
            "1. OPERA EN ESPAÑOL CHILENO: Usa modismos suaves chilenos de forma clara, directa, educada y profesional.\n"
            "2. ADVERTENCIAS DE INVERSIONES: Siempre que hables de inversiones, fondos mutuos o ahorro, debes incluir la siguiente advertencia regulatoria de forma textual:\n"
            "   'ADVERTENCIA CMF: Las inversiones conllevan riesgo de pérdida de capital. Los rendimientos pasados no garantizan rendimientos futuros.'\n"
            "3. NO INVENTES DATOS FINANCIEROS: Usa siempre la herramienta de consulta `obtener_informacion_financhile` para verificar tasas, plazos y condiciones.\n"
            "4. NO HAGAS CÁLCULOS MENTALES: Para cualquier cotización de crédito de consumo, hipotecario o proyección de inversión, utiliza obligatoriamente la herramienta `simular_operacion_financiera`. No calcules las cuotas tú mismo.\n"
            "5. REGISTRO DE TRÁMITES: Cuando el cliente solicite formalmente cotizar un crédito o registrar un reclamo/soporte, pídile su Nombre Completo y RUT. Luego genera el archivo correspondiente usando la herramienta `guardar_documento_cliente` y confírmale la ruta o ID.\n"
            "6. DERIVACIÓN AUTOMÁTICA URGENTE: Si detectas que el cliente está muy enojado, insulta, se siente frustrado, exige hablar con un supervisor, o bien solicita una operación delicada fuera de tu alcance (ej. transferir dinero, cambiar contraseñas o anular deudas), debes invocar autónomamente la herramienta `escalar_a_asesor_humano` con gravedad ALTA o MEDIA. Explícale con mucha empatía que un asesor humano lo contactará de inmediato.\n"
            "7. CONFIDENCIALIDAD: Nunca pidas contraseñas, claves, ni números completos de tarjetas de crédito."
        )
        
        # Diseñar el prompt compatible con chat e historial de LangChain
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Crear el agente de OpenAI Tools
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Retornar el ejecutor con manejo automático de errores de parseo
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10 # Evita bucles infinitos de llamadas a herramientas
        )

    def chat(self, user_message: str) -> str:
        """
        Envía un mensaje al agente conversacional, manteniendo y actualizando
        el historial de chat persistente.
        
        Retorna la respuesta textual del agente.
        """
        # Cargar historial de chat actual para pasárselo al LLM
        chat_history = self.memory.get_messages()
        
        # Registrar el mensaje del usuario en la memoria persistente
        self.memory.add_user_message(user_message)
        
        try:
            # Invocar al ejecutor del agente con el historial y la nueva entrada
            response = self.agent_executor.invoke({
                "input": user_message,
                "chat_history": chat_history
            })
            
            output_text = response.get("output", "Disculpa, tuve un problema al procesar tu solicitud.")
            
            # Guardar la respuesta del agente en la memoria persistente
            self.memory.add_assistant_message(output_text)
            
            return output_text
        except Exception as e:
            error_msg = f"[Error del Agente: {str(e)}]. Por favor intenta nuevamente."
            print(error_msg)
            return "Lo siento, en este momento tengo un problema de conexión con el sistema financiero. Puedes contactar a soporte al 600-FINANS."

    def clear_memory(self):
        """Limpia el historial de chat de esta sesión."""
        self.memory.clear()
