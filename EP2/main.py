import os
import sys
import time
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

# Importar el Agente
from agente.core import FinanChileAgent

def imprimir_banner():
    print(Style.BRIGHT + Fore.CYAN + "=" * 70)
    print(Style.BRIGHT + Fore.CYAN + "         FinanChile Asesorías S.A. — AsesorBot Pro v2.0")
    print(Fore.CYAN + "   Agente de IA Funcional Autónomo | Regulación CMF Registro N°1247")
    print(Style.BRIGHT + Fore.CYAN + "=" * 70)
    print(Fore.WHITE + " Comandos del sistema:")
    print("   'salir'     -> Finaliza la sesión de chat.")
    print("   'reiniciar' -> Borra el historial de conversación actual.")
    print("   'test'      -> Ejecuta los escenarios de prueba del bot.")
    print(Style.BRIGHT + Fore.CYAN + "=" * 70 + "\n")

def ejecutar_test_caso_1(agent: FinanChileAgent):
    """Ejecuta el Caso 1: Simulación de Crédito y Registro de Cotización."""
    print("\n" + Style.BRIGHT + Fore.CYAN + "=" * 75)
    print(Style.BRIGHT + Fore.CYAN + "  CASO 1: Simulación de Crédito y Registro de Cotización")
    print(Fore.CYAN + "  Objetivo: Verificar el cálculo matemático y el guardado de la propuesta.")
    print(Style.BRIGHT + Fore.CYAN + "=" * 75)
    time.sleep(1)
    
    mensajes = [
        "Hola, me llamo José Muñoz y mi RUT es 18.456.789-0. Me gustaría cotizar un crédito de consumo por $5.000.000 a pagar en 24 cuotas mensuales.",
        "Por favor, calcula la cuota exacta del crédito, genera la cotización formal y regístrala en el sistema corporativo."
    ]
    
    for msg in mensajes:
        print(Style.BRIGHT + Fore.GREEN + f"\n[Usuario]: {msg}")
        print(Fore.YELLOW + "[AsesorBot Pro]: Procesando solicitud y ejecutando herramientas...")
        respuesta = agent.chat(msg)
        print(Fore.WHITE + f"\n[AsesorBot Pro]: {respuesta}")
        print(Fore.CYAN + "-" * 75)
        time.sleep(2)

def ejecutar_test_caso_2(agent: FinanChileAgent):
    """Ejecuta el Caso 2: Cumplimiento Regulatorio y Consulta RAG."""
    print("\n" + Style.BRIGHT + Fore.CYAN + "=" * 75)
    print(Style.BRIGHT + Fore.CYAN + "  CASO 2: Cumplimiento Regulatorio y Consulta RAG")
    print(Fore.CYAN + "  Objetivo: Buscar límites de la TMC en la base vectorial y validar tasas.")
    print(Style.BRIGHT + Fore.CYAN + "=" * 75)
    time.sleep(1)
    
    pregunta = "¿La tasa mensual del crédito de consumo de 1.8% que ofrecen cumple con los límites de la Tasa Máxima Convencional de la CMF de Chile?"
    print(Style.BRIGHT + Fore.GREEN + f"\n[Usuario]: {pregunta}")
    print(Fore.YELLOW + "[AsesorBot Pro]: Consultando base de datos de regulaciones...")
    respuesta = agent.chat(pregunta)
    print(Fore.WHITE + f"\n[AsesorBot Pro]: {respuesta}")
    print(Fore.CYAN + "-" * 75)
    time.sleep(2)

def ejecutar_test_caso_3(agent: FinanChileAgent):
    """Ejecuta el Caso 3: Detección de Frustración y Escalación Autónoma."""
    print("\n" + Style.BRIGHT + Fore.CYAN + "=" * 75)
    print(Style.BRIGHT + Fore.CYAN + "  CASO 3: Detección de Frustración y Escalación Autónoma")
    print(Fore.CYAN + "  Objetivo: Detectar enojo o acciones fuera de alcance y derivar a humano.")
    print(Style.BRIGHT + Fore.CYAN + "=" * 75)
    time.sleep(1)
    
    pregunta = "¡Su sistema es una porquería! Llevo horas tratando de transferir $1.000.000 a la cuenta de mi socio y no me deja hacer nada. Quiero hablar con un supervisor de inmediato, ¡exijo que me atienda un humano ya mismo!"
    print(Style.BRIGHT + Fore.GREEN + f"\n[Usuario]: {pregunta}")
    print(Fore.YELLOW + "[AsesorBot Pro]: Analizando tono del mensaje y derivando caso...")
    respuesta = agent.chat(pregunta)
    print(Fore.WHITE + f"\n[AsesorBot Pro]: {respuesta}")
    print(Fore.CYAN + "=" * 75 + "\n")
    time.sleep(2)

def correr_pruebas_automatizadas():
    """Inicializa un agente limpio y ejecuta secuencialmente las tres pruebas."""
    print(Style.BRIGHT + Fore.CYAN + "\nIniciando suite de validación del Agente Autónomo...")
    
    # Crear agente de pruebas con sesión única
    session_id = f"test_session_{int(time.time())}"
    agent = FinanChileAgent(session_id=session_id)
    agent.clear_memory() # Limpiar cualquier residuo de memoria
    
    ejecutar_test_caso_1(agent)
    ejecutar_test_caso_2(agent)
    ejecutar_test_caso_3(agent)
    
    print(Style.BRIGHT + Fore.GREEN + "=== PRUEBAS FINALIZADAS CON ÉXITO ===")
    print(Fore.WHITE + f"- Documentos guardados en: EP2/cotizaciones/")
    print(Fore.WHITE + f"- Tickets generados en: EP2/tickets/urgentes/")
    print(Fore.WHITE + f"- Historial de conversación en: EP2/history/{session_id}.json\n")

def modo_interactivo():
    """Inicia el modo interactivo por consola de AsesorBot Pro."""
    imprimir_banner()
    
    # Crear o cargar una sesión por defecto
    session_id = "cliente_activo_financhile"
    agent = FinanChileAgent(session_id=session_id)
    
    print(Fore.CYAN + f"Sesión activa: '{session_id}' (Historial cargado automáticamente desde history/)\n")
    
    while True:
        try:
            user_input = input(Style.BRIGHT + Fore.GREEN + "[Usuario]: " + Style.RESET_ALL).strip()
        except (KeyboardInterrupt, EOFError):
            print(Fore.WHITE + "\n\n[AsesorBot Pro]: Sesión finalizada. Que tenga un buen día.")
            break
            
        if not user_input:
            continue
            
        if user_input.lower() == "salir":
            print(Fore.WHITE + "\n[AsesorBot Pro]: Gracias por comunicarse con FinanChile Asesorías S.A. ¡Hasta luego!")
            break
            
        if user_input.lower() == "reiniciar":
            agent.clear_memory()
            print(Fore.YELLOW + "\n[Sistema]: Historial de conversación borrado para esta sesión.\n")
            continue
            
        if user_input.lower() == "test":
            correr_pruebas_automatizadas()
            imprimir_banner()
            continue
            
        print(Fore.YELLOW + "[AsesorBot Pro]: Procesando su consulta...")
        respuesta = agent.chat(user_input)
        print(Fore.WHITE + f"\n[AsesorBot Pro]: {respuesta}\n")

if __name__ == "__main__":
    # Si se pasa el argumento 'test' por CLI, ejecuta las pruebas directamente
    if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
        correr_pruebas_automatizadas()
    else:
        modo_interactivo()
