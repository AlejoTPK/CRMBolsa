import os
import json
import yfinance as yf
from groq import AsyncGroq
from dotenv import load_dotenv
from api.models.recommendations import RecomendacionIA

load_dotenv()

_groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# Mapping of tickers to Yahoo Finance symbols
TICKER_MAP = {
    "XAU": "GC=F",
    "WTI": "CL=F",
}

def _get_recent_context(ticker: str) -> dict:
    """Obtiene un contexto reciente simple usando yfinance para pasarlo al LLM."""
    simbolo_yf = TICKER_MAP.get(ticker.upper())
    if not simbolo_yf:
        raise ValueError(f"Ticker {ticker} no soportado para análisis.")
    
    yf_ticker = yf.Ticker(simbolo_yf)
    hist = yf_ticker.history(period="5d")
    
    if hist.empty:
        return {"error": "No hay datos recientes."}
    
    # Extraemos el último cierre y el cierre de hace 5 días para tener un contexto simple
    precio_actual = round(float(hist["Close"].iloc[-1]), 2)
    precio_5d = round(float(hist["Close"].iloc[0]), 2)
    variacion_pct = round(((precio_actual - precio_5d) / precio_5d) * 100, 2)
    
    return {
        "precio_actual": precio_actual,
        "precio_hace_5_dias": precio_5d,
        "variacion_5d_pct": variacion_pct,
        "direccion": "alcista" if variacion_pct > 0 else "bajista" if variacion_pct < 0 else "lateral"
    }

async def generar_recomendacion(ticker: str) -> RecomendacionIA:
    """
    Construye el prompt con contexto real, inyecta la petición a Groq
    y retorna el modelo validado RecomendacionIA.
    """
    contexto = _get_recent_context(ticker)
    
    if "error" in contexto:
        raise RuntimeError("No se pudo obtener el contexto del mercado para analizar.")
        
    nombre_activo = "Oro (XAU/USD)" if ticker.upper() == "XAU" else "Petróleo Crudo (WTI)"
    
    prompt = f"""
    Eres el analista de IA experto de "Sovereign CRM", enfocado en enseñar a inversores novatos.
    El usuario solicita una sugerencia pedagógica sobre {nombre_activo}.
    
    CONTEXTO RECIENTE (Últimos 5 días):
    - Precio Actual: ${contexto["precio_actual"]}
    - Precio hace 5 días: ${contexto["precio_hace_5_dias"]}
    - Variación en 5 días: {contexto["variacion_5d_pct"]}% ({contexto["direccion"]})
    
    REGLAS DE RESPUESTA:
    - Responde ÚNICAMENTE con un objeto JSON válido.
    - El JSON debe tener exactamente estos campos:
      - "ticker": string (debe ser "{ticker.upper()}")
      - "tendencia_corta": string ("ALCISTA", "BAJISTA" o "LATERAL")
      - "sugerencias_pedagogicas": array de strings (Lista de al menos 2 sugerencias u observaciones educativas fáciles de entender sobre qué hacer o mirar)
      - "disclaimer_obligatorio": string (Obligatorio escribir: "Solo con fines educativos, no es asesoría financiera.")
    """
    
    chat_completion = await _groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente financiero pedagógico. Respondes exclusivamente en formato JSON."
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.5,
        max_tokens=500,
    )
    
    respuesta_json = chat_completion.choices[0].message.content
    datos = json.loads(respuesta_json)
    
    return RecomendacionIA(**datos)
