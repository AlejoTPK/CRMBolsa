"""
Sovereign Insights — Servicio de IA y Alertas
Archivo: api/services/insights_service.py

Contiene:
- La tarea en segundo plano que revisa anomalías cada 30 minutos.
- La lógica para generar el Resumen Diario usando yfinance + LLM.
"""
import asyncio
import datetime
import json
import os
import random
from typing import Optional

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from groq import AsyncGroq

from api.models.insights import AlertaMercado, ResumenDiario, LeccionDelDia

load_dotenv()

# ---------------------------------------------------------------------------
# IMPLEMENTACIÓN REAL: Groq (llama-3.3-70b-versatile)
# ---------------------------------------------------------------------------
_groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def call_llm(prompt: str) -> str:
    """
    Llama a la API de Groq con el modelo llama-3.3-70b-versatile.
    Retorna el contenido de la respuesta como string JSON.
    
    - response_format json_object: garantiza que Groq devuelva JSON válido.
    - temperature 0.4: respuestas precisas pero con algo de naturalidad narrativa.
    - max_tokens 1024: suficiente para los JSONs de alertas y resúmenes.
    """
    chat_completion = await _groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres el motor de análisis financiero de 'Sovereign CRM'. "
                    "Siempre respondes ÚNICAMENTE con JSON válido, sin markdown, "
                    "sin texto adicional antes o después del JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=1024,
    )
    return chat_completion.choices[0].message.content



# ---------------------------------------------------------------------------
# Estado en memoria para la última alerta (compartido entre requests)
# En producción, esto se persistiría en Supabase.
# ---------------------------------------------------------------------------
_ultima_alerta_cache: Optional[AlertaMercado] = None
_ultimo_precio_cache: dict[str, float] = {}


def _get_precio_actual(simbolo_yf: str) -> float:
    """Obtiene el precio de cierre más reciente de un símbolo de yfinance."""
    ticker = yf.Ticker(simbolo_yf)
    hist = ticker.history(period="1d", interval="5m")
    if hist.empty:
        return 0.0
    return float(hist["Close"].iloc[-1])


# ---------------------------------------------------------------------------
# MÓDULO 1A: TAREA EN SEGUNDO PLANO — Monitor de Anomalías (cada 30 min)
# ---------------------------------------------------------------------------

COMMODITIES_MONITOR = {
    "XAU": "GC=F",
    "WTI": "CL=F",
}
UMBRAL_VARIACION_PCT = 2.0  # Alerta si el precio varía más de ±2%


async def _revisar_anomalia_precio():
    """
    Lógica central de la tarea en segundo plano.
    Compara el precio actual con el último precio cacheado.
    Si la variación supera el umbral, llama al LLM y genera una AlertaMercado.
    """
    global _ultima_alerta_cache, _ultimo_precio_cache

    for codigo, simbolo_yf in COMMODITIES_MONITOR.items():
        try:
            precio_actual = _get_precio_actual(simbolo_yf)
            if precio_actual == 0.0:
                continue

            precio_anterior = _ultimo_precio_cache.get(codigo, precio_actual)
            variacion_pct = ((precio_actual - precio_anterior) / precio_anterior) * 100

            print(
                f"[Insights Monitor] {codigo}: Precio={precio_actual:.2f}, "
                f"Variación={variacion_pct:+.2f}%"
            )

            if abs(variacion_pct) >= UMBRAL_VARIACION_PCT:
                # --- Construir el prompt para el LLM ---
                direccion = "subida" if variacion_pct > 0 else "caída"
                severidad_sugerida = "CRITICO" if abs(variacion_pct) >= 4 else "MODERADO"

                prompt = f"""
Eres el motor de análisis de "Sovereign", un CRM financiero para inversores novatos.
Detectamos una anomalía de mercado. Genera una alerta pedagógica en JSON estricto.

DATOS DE MERCADO:
- Activo: {codigo} ({'Oro XAU/USD' if codigo == 'XAU' else 'Petróleo Crudo WTI'})
- Precio anterior (hace 30 min): ${precio_anterior:.2f}
- Precio actual: ${precio_actual:.2f}
- Variación: {variacion_pct:+.2f}% ({direccion})
- Severidad sugerida: {severidad_sugerida}

REGLAS DE RESPUESTA:
- Responde ÚNICAMENTE con un objeto JSON válido. Sin markdown, sin explicaciones.
- El JSON debe tener exactamente estos campos:
  - "tipo_alerta": string (debe ser "{codigo}")
  - "titulo": string (máximo 80 caracteres, titular impactante)
  - "mensaje": string (2-3 oraciones, lenguaje simple para novatos, explica QUÉ pasó y QUÉ significa)
  - "nivel_severidad": string (debe ser uno de: "INFORMATIVO", "MODERADO", "CRITICO")

EJEMPLO DE FORMATO:
{{"tipo_alerta": "{codigo}", "titulo": "...", "mensaje": "...", "nivel_severidad": "{severidad_sugerida}"}}
"""
                try:
                    respuesta_llm = await call_llm(prompt)
                    datos_alerta = json.loads(respuesta_llm)
                    alerta = AlertaMercado(**datos_alerta)
                    _ultima_alerta_cache = alerta
                    print(f"[Insights Monitor] ✅ Alerta generada: {alerta.titulo}")
                except Exception as e:
                    print(f"[Insights Monitor] ❌ Error al generar alerta LLM: {e}")

            # Actualizar el caché de precios
            _ultimo_precio_cache[codigo] = precio_actual

        except Exception as e:
            print(f"[Insights Monitor] ❌ Error al revisar {codigo}: {e}")


async def monitor_loop():
    """
    Bucle infinito que ejecuta la revisión de anomalías cada 30 minutos.
    Se lanza como background task en el startup de FastAPI.
    """
    print("[Insights Monitor] 🔄 Monitor de anomalías iniciado. Revisión cada 30 min.")
    while True:
        await _revisar_anomalia_precio()
        await asyncio.sleep(30 * 60)  # 30 minutos


def get_ultima_alerta() -> Optional[AlertaMercado]:
    """Getter para que el router acceda a la última alerta cacheada."""
    return _ultima_alerta_cache


# ---------------------------------------------------------------------------
# MÓDULO 1B: RESUMEN DIARIO — Batch Processing al cierre del mercado
# ---------------------------------------------------------------------------

def _recopilar_datos_jornada() -> dict:
    """
    Usa yfinance y Pandas para obtener los datos OHLCV de la jornada.
    Retorna un diccionario con apertura, cierre y variación para cada activo.
    """
    resultado = {}
    hoy = datetime.date.today().strftime("%Y-%m-%d")

    simbolos = {"XAU": "GC=F", "WTI": "CL=F"}
    for codigo, simbolo_yf in simbolos.items():
        try:
            ticker = yf.Ticker(simbolo_yf)
            hist = ticker.history(period="1d")

            if hist.empty:
                resultado[codigo] = {"error": "Sin datos para hoy"}
                continue

            # Usamos Pandas para calcular métricas de la jornada
            df: pd.DataFrame = hist

            apertura = round(float(df["Open"].iloc[0]), 2)
            cierre = round(float(df["Close"].iloc[-1]), 2)
            maximo = round(float(df["High"].max()), 2)
            minimo = round(float(df["Low"].min()), 2)
            variacion_pct = round(((cierre - apertura) / apertura) * 100, 2)
            volumen = int(df["Volume"].sum())

            resultado[codigo] = {
                "fecha": hoy,
                "apertura": apertura,
                "cierre": cierre,
                "maximo": maximo,
                "minimo": minimo,
                "variacion_pct": variacion_pct,
                "volumen": volumen,
                "direccion": "📈 alza" if variacion_pct > 0 else "📉 baja"
            }
        except Exception as e:
            resultado[codigo] = {"error": str(e)}

    return resultado


async def generar_resumen_diario() -> ResumenDiario:
    """
    Orquesta la generación del Resumen Diario:
    1. Recopila datos reales de yfinance con Pandas.
    2. Construye un prompt rico en contexto para el LLM.
    3. Valida la respuesta del LLM con Pydantic.
    4. Retorna un objeto ResumenDiario listo para guardarse en Supabase.
    """
    datos = _recopilar_datos_jornada()
    hoy = datetime.date.today().strftime("%Y-%m-%d")

    # Formatear datos para el prompt
    def _fmt(d: dict, nombre: str) -> str:
        if "error" in d:
            return f"  {nombre}: Error al obtener datos ({d['error']})"
        return (
            f"  {nombre}:\n"
            f"    - Apertura: ${d['apertura']:.2f}\n"
            f"    - Cierre: ${d['cierre']:.2f}\n"
            f"    - Máximo: ${d['maximo']:.2f} / Mínimo: ${d['minimo']:.2f}\n"
            f"    - Variación: {d['variacion_pct']:+.2f}% ({d['direccion']})\n"
            f"    - Volumen: {d['volumen']:,}"
        )

    contexto_xau = _fmt(datos.get("XAU", {"error": "Sin datos"}), "ORO (XAU/USD)")
    contexto_wti = _fmt(datos.get("WTI", {"error": "Sin datos"}), "PETRÓLEO (WTI)")

    conceptos_leccion = [
        "El interés compuesto",
        "Diversificación de portafolios",
        "Qué es la inflación y cómo afecta las inversiones",
        "La relación entre el dólar y las materias primas",
        "El ciclo económico y los commodities",
        "Diferencia entre Análisis Técnico y Análisis Fundamental",
        "El riesgo sistemático vs no sistemático",
        "Qué es el volumen de trading y por qué importa",
        "El efecto de las tasas de interés en los mercados",
        "Bulls (Toros) vs Bears (Osos): Psicología del mercado"
    ]
    tema_leccion = random.choice(conceptos_leccion)

    prompt = f"""
Eres el analista de "Sovereign", un CRM financiero pedagógico para inversores novatos.
Tu misión es generar el Resumen Diario del mercado, combinando los datos reales del día
con explicaciones claras y educativas. Hoy es {hoy}.

DATOS REALES DE LA JORNADA (fuente: yfinance):
{contexto_xau}
{contexto_wti}

REGLAS DE RESPUESTA:
- Responde ÚNICAMENTE con un objeto JSON válido. Sin markdown, sin texto extra.
- El JSON debe tener exactamente estos campos:
  - "fecha_resumen": string (formato YYYY-MM-DD, usa la fecha de hoy: "{hoy}")
  - "titulo_jornada": string (titular creativo que capturen el sentimiento del día)
  - "resumen_oro": string (2-3 oraciones, análisis del XAU/USD en lenguaje simple)
  - "resumen_petroleo": string (2-3 oraciones, análisis del WTI en lenguaje simple)
  - "leccion_del_dia": objeto con:
      - "concepto": string (Debe estar obligatoriamente relacionado con el tema: "{tema_leccion}")
      - "explicacion": string (explicación de 3-4 oraciones sobre "{tema_leccion}", sin jerga, para un principiante, usando alguna analogía interesante)

IMPORTANTE: El tono debe ser informativo pero cálido. El lector es un novato que quiere
aprender finanzas, no un trader experto. NUNCA repitas lecciones de días anteriores. Sé original.
"""

    respuesta_llm = await call_llm(prompt)
    datos_resumen = json.loads(respuesta_llm)

    # Pydantic valida la estructura antes de retornar
    resumen = ResumenDiario(**datos_resumen)
    return resumen
