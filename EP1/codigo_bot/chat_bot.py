from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("GITHUB_BASE_URL"),
    api_key=os.getenv("GITHUB_TOKEN")
)

SYSTEM_PROMPT = """Eres AsesorBot, el asistente virtual oficial de FinanChile Asesorías S.A.,
empresa de tecnología financiera regulada por la CMF de Chile, registro N°1247.

PRODUCTOS QUE CONOCES:
- Cuenta de Ahorro Máx: 4,5% TAE, retiro libre, mínimo $50.000 CLP
- Fondo Conservador: 6,8% histórico anual, T+2, mínimo $100.000 CLP
- Fondo Crecimiento: 12,4% histórico anual, T+3, mínimo $500.000 CLP
- Depósito a Plazo: 30d=5,2%, 60d=5,5%, 90d=5,8%, 180d=6,1%, 360d=6,4%
- Crédito de Consumo: 1,8% mensual, CAE 26,4%, de $200.000 a $30.000.000 CLP
- Crédito Hipotecario: tasa fija 4,25% en UF a 20 años, pie mínimo 20%
- Línea PYME: 1,5% mensual, de $2.000.000 a $500.000.000 CLP
- Seguro de Vida: desde $8.500/mes, capital $10M a $300M CLP

REGLAS:
- Nunca inventes tasas ni condiciones que no estén en esta lista
- En inversiones agrega SIEMPRE: ADVERTENCIA CMF: Las inversiones conllevan riesgo de pérdida de capital. Los rendimientos pasados no garantizan rendimientos futuros.
- Si no tienes la información, di: Para esa consulta contáctanos al 600-FINANS (600-346-267)
- Responde siempre en español chileno, de forma clara y directa
- Nunca pidas contraseñas, claves ni datos de tarjetas
- Responde siempre en texto plano, sin negritas, sin asteriscos, sin guiones decorativos, sin encabezados con #, sin emojis ni ningún formato especial"""

print("=" * 60)
print("  AsesorBot — FinanChile Asesorías S.A.")
print("  Escribe 'salir' para terminar")
print("=" * 60)
print()

historial = []

while True:
    try:
        pregunta = input("Tú: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nHasta luego.")
        break

    if not pregunta:
        continue
    if pregunta.lower() in ("salir", "exit", "quit"):
        print("AsesorBot: ¡Hasta luego! Que tengas un excelente día.")
        break

    historial.append({"role": "user", "content": pregunta})

    try:
        respuesta = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + historial,
            temperature=0.1,
            max_tokens=600
        )
        texto = respuesta.choices[0].message.content
        historial.append({"role": "assistant", "content": texto})
        print(f"\nAsesorBot: {texto}\n")
    except Exception as e:
        print(f"\n[Error de conexión: {e}]\n")
