import os
import json
from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Configuración de rutas y directorios
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
COTIZACIONES_DIR = BASE_DIR / "cotizaciones"
TICKETS_DIR = BASE_DIR / "tickets"

# Asegurar directorios
COTIZACIONES_DIR.mkdir(parents=True, exist_ok=True)
TICKETS_DIR.mkdir(parents=True, exist_ok=True)
(TICKETS_DIR / "urgentes").mkdir(parents=True, exist_ok=True)

# Instanciar embeddings y vectorstore de forma perezosa
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        # Configuración para usar GitHub Models
        api_base = os.getenv("GITHUB_BASE_URL", "https://models.inference.ai.azure.com")
        token = os.getenv("GITHUB_TOKEN", "")
        
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_base=api_base,
            openai_api_key=token
        )
        
        # Carga del VectorStore FAISS guardado localmente
        if VECTORSTORE_DIR.exists():
            _vector_store = FAISS.load_local(
                folder_path=str(VECTORSTORE_DIR),
                embeddings=embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            raise FileNotFoundError(
                f"No se encontró el índice vectorial en {VECTORSTORE_DIR}. "
                "Asegúrate de haber copiado la carpeta financhile_vectorstore a EP2/vectorstore/."
            )
    return _vector_store


# =====================================================================
# 1. HERRAMIENTA DE CONSULTA (RAG Semantic Context Recovery)
# =====================================================================
@tool
def obtener_informacion_financhile(query: str) -> str:
    """
    Busca información oficial en el Manual de Productos Financieros, Preguntas Frecuentes (FAQs), 
    Políticas de la Empresa y Regulaciones de la CMF. 
    Úsalo siempre que necesites conocer tasas de interés, plazos, requisitos, políticas internas 
    o normas legales de FinanChile.
    """
    try:
        store = get_vector_store()
        # Buscar los 4 fragmentos más relevantes
        docs = store.similarity_search(query, k=4)
        
        resultados = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Documento Interno")
            source_type = doc.metadata.get("source_type", "interno")
            content = doc.page_content.strip()
            resultados.append(
                f"--- FRAGMENTO {i} (Origen: {source} | Tipo: {source_type}) ---\n"
                f"{content}\n"
            )
        
        contexto = "\n".join(resultados)
        return (
            f"Resultados de la búsqueda semántica en FinanChile para '{query}':\n\n"
            f"{contexto}\n"
            "INSTRUCCIÓN PARA EL AGENTE: Utiliza estos datos para responder de forma precisa y "
            "siempre cita el origen del fragmento en corchetes al final de tu respuesta (ej: [Manual de Productos Financieros])."
        )
    except Exception as e:
        return f"Error al consultar el almacén de conocimiento: {str(e)}"


# =====================================================================
# 2. HERRAMIENTA DE RAZONAMIENTO (Financial Calculator)
# =====================================================================
@tool
def simular_operacion_financiera(producto: str, monto: float, plazo_meses: int) -> str:
    """
    Simula de forma exacta operaciones financieras de créditos de consumo, créditos hipotecarios, 
    cuentas de ahorro y fondos mutuos de FinanChile. Evita errores matemáticos del modelo.
    
    Parámetros:
    - producto: El producto a simular. Debe ser exactamente uno de los siguientes:
      'credito_consumo', 'credito_hipotecario', 'cuenta_ahorro_max', 'fondo_conservador', 'fondo_crecimiento'.
    - monto: Monto en pesos chilenos (CLP) a solicitar o invertir.
    - plazo_meses: Plazo de la operación en meses (ej: 12, 24, 36 para consumo; 120, 240 para hipotecario).
    """
    producto = producto.lower().strip()
    
    # 1. CRÉDITO DE CONSUMO
    if "consumo" in producto:
        # Tasa mensual fija de FinanChile: 1.8% (0.018)
        tasa_mensual = 0.018
        # Fórmula de cuota mensual fija (Amortización Francesa)
        # R = P * (i * (1+i)^n) / ((1+i)^n - 1)
        try:
            cuota = monto * (tasa_mensual * ((1 + tasa_mensual) ** plazo_meses)) / (((1 + tasa_mensual) ** plazo_meses) - 1)
            costo_total = cuota * plazo_meses
            interes_total = costo_total - monto
            
            # Estimación de la CMF para el CAE (Costo Anual Equivalente) aproximado
            # En base a la tasa de 1.8% mensual, el CAE es aproximadamente 26.4% anual
            cae = 26.4
            
            resultado = {
                "producto": "Crédito de Consumo FinanChile",
                "monto_solicitado_clp": monto,
                "plazo_meses": plazo_meses,
                "tasa_interes_mensual": "1.8%",
                "tasa_interes_anual_nominal": "21.6%",
                "cae_anual_estimado": "26.4%",
                "cuota_mensual_clp": round(cuota),
                "costo_total_credito_clp": round(costo_total),
                "intereses_totales_clp": round(interes_total),
                "advertencia_legal": "El otorgamiento del crédito está sujeto a evaluación crediticia comercial por FinanChile Asesorías S.A."
            }
            return json.dumps(resultado, ensure_ascii=False, indent=2)
        except ZeroDivisionError:
            return "Error: El plazo en meses debe ser mayor a 0."

    # 2. CRÉDITO HIPOTECARIO
    elif "hipotecario" in producto:
        # Tasa anual fija en UF: 4.25% (0.0425). Valor UF Enero 2025: $38.453,21 CLP
        valor_uf = 38453.21
        tasa_anual_uf = 0.0425
        tasa_mensual_uf = tasa_anual_uf / 12
        
        monto_uf = monto / valor_uf
        pie_minimo_uf = monto_uf * 0.20
        pie_minimo_clp = monto * 0.20
        
        try:
            # Cuota mensual en UF
            cuota_uf = monto_uf * (tasa_mensual_uf * ((1 + tasa_mensual_uf) ** plazo_meses)) / (((1 + tasa_mensual_uf) ** plazo_meses) - 1)
            cuota_clp = cuota_uf * valor_uf
            costo_total_uf = cuota_uf * plazo_meses
            costo_total_clp = costo_total_uf * valor_uf
            interes_total_uf = costo_total_uf - monto_uf
            interes_total_clp = interes_total_uf * valor_uf
            
            resultado = {
                "producto": "Crédito Hipotecario en UF FinanChile",
                "monto_propiedad_clp": monto,
                "monto_propiedad_uf": round(monto_uf, 2),
                "pie_minimo_requerido_20_clp": round(pie_minimo_clp),
                "pie_minimo_requerido_20_uf": round(pie_minimo_uf, 2),
                "monto_a_financiar_80_uf": round(monto_uf * 0.80, 2),
                "plazo_meses": plazo_meses,
                "plazo_anos": round(plazo_meses / 12, 1),
                "tasa_anual_uf": "4.25%",
                "tasa_mensual_uf": f"{round(tasa_mensual_uf * 100, 3)}%",
                "valor_uf_referencia": valor_uf,
                "cuota_mensual_uf": round(cuota_uf, 2),
                "cuota_mensual_estimada_clp": round(cuota_clp),
                "costo_total_hipoteca_uf": round(costo_total_uf, 2),
                "costo_total_estimado_clp": round(costo_total_clp),
                "intereses_totales_uf": round(interes_total_uf, 2),
                "intereses_totales_estimados_clp": round(interes_total_clp),
                "advertencia_legal": "FinanChile exige un pie mínimo del 20%. Los valores en CLP son referenciales debido a la variación diaria de la UF."
            }
            return json.dumps(resultado, ensure_ascii=False, indent=2)
        except ZeroDivisionError:
            return "Error: El plazo en meses debe ser mayor a 0."

    # 3. CUENTA DE AHORRO MÁX
    elif "ahorro" in producto:
        # Tasa Anual Equivalente (TAE): 4.5% (0.045)
        tasa_anual = 0.045
        rendimiento_estimado = monto * ((1 + tasa_anual) ** (plazo_meses / 12)) - monto
        monto_final = monto + rendimiento_estimado
        
        resultado = {
            "producto": "Cuenta de Ahorro Máx FinanChile",
            "monto_invertido_clp": monto,
            "plazo_meses": plazo_meses,
            "tasa_anual_tae": "4.5%",
            "rendimiento_estimado_clp": round(rendimiento_estimado),
            "monto_final_estimado_clp": round(monto_final),
            "advertencia_legal": "ADVERTENCIA CMF: Las inversiones conllevan riesgo de pérdida de capital. Los rendimientos pasados no garantizan rendimientos futuros."
        }
        return json.dumps(resultado, ensure_ascii=False, indent=2)

    # 4. FONDO CONSERVADOR
    elif "conservador" in producto:
        # Rendimiento histórico anual: 6.8% (0.068)
        tasa_anual = 0.068
        rendimiento_estimado = monto * ((1 + tasa_anual) ** (plazo_meses / 12)) - monto
        monto_final = monto + rendimiento_estimado
        
        resultado = {
            "producto": "Fondo Mutuo Conservador FinanChile",
            "monto_invertido_clp": monto,
            "plazo_meses": plazo_meses,
            "rendimiento_historico_anual": "6.8%",
            "rendimiento_estimado_clp": round(rendimiento_estimado),
            "monto_final_estimado_clp": round(monto_final),
            "tiempo_rescate": "T+2 (48 horas hábiles)",
            "advertencia_legal": "ADVERTENCIA CMF: Las inversiones conllevan riesgo de pérdida de capital. Los rendimientos pasados no garantizan rendimientos futuros."
        }
        return json.dumps(resultado, ensure_ascii=False, indent=2)

    # 5. FONDO CRECIMIENTO
    elif "crecimiento" in producto:
        # Rendimiento histórico anual: 12.4% (0.124)
        tasa_anual = 0.124
        rendimiento_estimado = monto * ((1 + tasa_anual) ** (plazo_meses / 12)) - monto
        monto_final = monto + rendimiento_estimado
        
        resultado = {
            "producto": "Fondo Mutuo Crecimiento FinanChile",
            "monto_invertido_clp": monto,
            "plazo_meses": plazo_meses,
            "rendimiento_historico_anual": "12.4%",
            "rendimiento_estimado_clp": round(rendimiento_estimado),
            "monto_final_estimado_clp": round(monto_final),
            "tiempo_rescate": "T+3 (72 horas hábiles)",
            "advertencia_legal": "ADVERTENCIA CMF: Las inversiones conllevan riesgo de pérdida de capital. Los rendimientos pasados no garantizan rendimientos futuros."
        }
        return json.dumps(resultado, ensure_ascii=False, indent=2)
        
    else:
        return (
            f"Error: El producto '{producto}' no es reconocido. "
            "Usa exactamente uno de los siguientes: 'credito_consumo', 'credito_hipotecario', "
            "'cuenta_ahorro_max', 'fondo_conservador', 'fondo_crecimiento'."
        )


# =====================================================================
# 3. HERRAMIENTA DE ESCRITURA (Proposal and Support Ticket Creator)
# =====================================================================
@tool
def guardar_documento_cliente(tipo_documento: str, nombre_cliente: str, rut_cliente: str, contenido_documento: str) -> str:
    """
    Crea y guarda documentos formales para el cliente en el almacenamiento local 
    (simulando el CRM de FinanChile). Genera cotizaciones detalladas o tickets de soporte.
    
    Parámetros:
    - tipo_documento: Tipo del archivo a guardar. Debe ser 'cotizacion' o 'ticket_soporte'.
    - nombre_cliente: Nombre completo del cliente (ej: 'Jose Munoz').
    - rut_cliente: RUT del cliente chileno con guión y dígito verificador (ej: '18.456.789-0').
    - contenido_documento: El texto estructurado del documento que se guardará.
    """
    tipo_documento = tipo_documento.lower().strip()
    
    # Sanitizar nombres de archivos
    nombre_normalizado = "".join(c for c in nombre_cliente if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_").lower()
    rut_normalizado = rut_cliente.replace(".", "").replace(" ", "").lower()
    fecha_hoy = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if "cotizacion" in tipo_documento or "cotización" in tipo_documento:
        filename = f"cotizacion_{nombre_normalizado}_{rut_normalizado}_{fecha_hoy}.txt"
        file_path = COTIZACIONES_DIR / filename
        
        encabezado = (
            "=================================================================\n"
            "         COTIZACIÓN FORMAL DE SERVICIO — FINANCHILE ASESORÍAS S.A.\n"
            f"         Fecha de Emisión: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            "=================================================================\n"
            f"CLIENTE: {nombre_cliente}\n"
            f"RUT: {rut_cliente}\n"
            "-----------------------------------------------------------------\n\n"
        )
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(encabezado + contenido_documento)
            
            return (
                f"✅ Cotización guardada con éxito en el CRM local de FinanChile.\n"
                f"Ruta de archivo: {file_path.absolute()}\n"
                f"Nombre del archivo: {filename}\n"
                "INSTRUCCIÓN PARA EL AGENTE: Confirma al cliente que su cotización formal ha sido "
                "registrada con éxito en el sistema corporativo, y proporciónale un resumen "
                "de los datos guardados de forma clara."
            )
        except Exception as e:
            return f"Error al escribir la cotización en disco: {str(e)}"
            
    elif "ticket" in tipo_documento or "soporte" in tipo_documento:
        filename = f"ticket_{rut_normalizado}_{fecha_hoy}.txt"
        file_path = TICKETS_DIR / filename
        
        encabezado = (
            "=================================================================\n"
            "         TICKET DE ATENCIÓN DE CLIENTES — FINANCHILE ASESORÍAS S.A.\n"
            f"         Fecha de Registro: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            "=================================================================\n"
            f"CLIENTE: {nombre_cliente}\n"
            f"RUT: {rut_cliente}\n"
            "-----------------------------------------------------------------\n\n"
        )
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(encabezado + contenido_documento)
                
            return (
                f"✅ Ticket de soporte registrado exitosamente en el sistema.\n"
                f"Ruta de archivo: {file_path.absolute()}\n"
                f"ID del ticket: TKT-{fecha_hoy}\n"
                "INSTRUCCIÓN PARA EL AGENTE: Entrega el código de seguimiento (TKT-...) al cliente "
                "y confírmale que su solicitud ha sido ingresada para revisión."
            )
        except Exception as e:
            return f"Error al escribir el ticket en disco: {str(e)}"
    else:
        return (
            f"Error: Tipo de documento '{tipo_documento}' no soportado. "
            "Usa 'cotizacion' o 'ticket_soporte'."
        )


# =====================================================================
# 4. HERRAMIENTA DE ESCALACIÓN (Decision Making / Human Hand-off)
# =====================================================================
@tool
def escalar_a_asesor_humano(nombre_cliente: str, rut_cliente: str, motivo: str, detalle: str, gravedad: str) -> str:
    """
    Decide derivar y escalar de forma prioritaria el caso del cliente a un asesor humano experto.
    Úsalo de forma autónoma ante las siguientes condiciones:
    1. Si el cliente demuestra un alto nivel de frustración, enojo o disconformidad severa en sus mensajes.
    2. Si el cliente solicita realizar una transacción fuera de las capacidades del bot (ej. transferencias bancarias,
       renegociar deudas complejas, cambiar contraseñas o solicitar claves de seguridad).
    3. Si se detecta un posible conflicto de cumplimiento regulatorio con la CMF que requiere criterio experto.
    
    Parámetros:
    - nombre_cliente: Nombre completo del cliente (ej: 'Jose Munoz').
    - rut_cliente: RUT del cliente (ej: '18.456.789-0').
    - motivo: Razón de la derivación. Debe ser claro y resumido (ej: 'Insatisfacción severa', 'Solicitud fuera de alcance').
    - detalle: Resumen de la conversación y del problema a resolver por el asesor.
    - gravedad: Nivel de urgencia. Debe ser 'media' o 'alta'.
    """
    gravedad = gravedad.lower().strip()
    if gravedad not in ("media", "alta"):
        gravedad = "media"
        
    rut_normalizado = rut_cliente.replace(".", "").replace(" ", "").lower()
    fecha_hoy = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticket_id = f"ESC-{fecha_hoy}"
    filename = f"escalacion_{rut_normalizado}_{fecha_hoy}.txt"
    file_path = TICKETS_DIR / "urgentes" / filename
    
    contenido = (
        "=================================================================\n"
        "      🚨 ESCALACIÓN PRIORITARIA A ASESOR HUMANO — FINANCHILE S.A.\n"
        f"      ID de Escalación: {ticket_id}\n"
        f"      Fecha y Hora de Derivación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        f"      Gravedad / Prioridad: {gravedad.upper()}\n"
        "=================================================================\n"
        f"DATOS DEL CLIENTE:\n"
        f"  - Nombre: {nombre_cliente}\n"
        f"  - RUT: {rut_cliente}\n"
        "\n"
        f"MOTIVO DE LA ESCALACIÓN:\n"
        f"  {motivo}\n"
        "\n"
        f"DETALLE DEL CASO Y CONVERSACIÓN:\n"
        f"  {detalle}\n"
        "-----------------------------------------------------------------\n"
        "ACCION REQUERIDA: Contactar al cliente de forma prioritaria en un plazo "
        "máximo de 15 minutos.\n"
        "=================================================================\n"
    )
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(contenido)
            
        return (
            f"🚨 DERIVACIÓN AUTÓNOMA EXITOSA.\n"
            f"El caso ha sido clasificado con prioridad {gravedad.upper()} e ingresado a la "
            f"cola de derivación humana de FinanChile con el ID de urgencia: {ticket_id}.\n"
            f"Archivo de escalación generado: {file_path.absolute()}\n\n"
            "INSTRUCCIÓN PARA EL AGENTE: Informa al cliente con empatía y profesionalismo que su caso "
            "ha sido derivado en este momento a un asesor especialista humano prioritario. Proporciónale "
            f"el ID de derivación {ticket_id} y dile que será contactado de inmediato por su canal preferido."
        )
    except Exception as e:
        return f"Error al registrar la escalación en el CRM corporativo: {str(e)}"
