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
from db.database import async_session
from db.models import DBAlertaMercado, DBResumenDiario

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
    - temperature 0.3: respuestas precisas y técnicas, evitando redundancias filosóficas.
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
        temperature=0.3,
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
                    
                    # Persistencia en Base de Datos (PostgreSQL)
                    async with async_session() as session:
                        db_alerta = DBAlertaMercado(
                            tipo_alerta=alerta.tipo_alerta,
                            titulo=alerta.titulo,
                            mensaje=alerta.mensaje,
                            nivel_severidad=alerta.nivel_severidad
                        )
                        session.add(db_alerta)
                        await session.commit()
                        
                    print(f"[Insights Monitor] ✅ Alerta generada y guardada: {alerta.titulo}")
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

    # Persistencia en Base de Datos (PostgreSQL)
    try:
        async with async_session() as session:
            db_resumen = DBResumenDiario(
                fecha_resumen=datetime.datetime.strptime(resumen.fecha_resumen, "%Y-%m-%d").date(),
                titulo_jornada=resumen.titulo_jornada,
                resumen_oro=resumen.resumen_oro,
                resumen_petroleo=resumen.resumen_petroleo,
                leccion_concepto=resumen.leccion_del_dia.concepto,
                leccion_explicacion=resumen.leccion_del_dia.explicacion
            )
            session.add(db_resumen)
            await session.commit()
            print(f"[Insights Service] ✅ Resumen diario guardado en DB para la fecha {resumen.fecha_resumen}")
    except Exception as e:
        print(f"[Insights Service] ⚠️ Error al persistir resumen en DB: {e}")

    return resumen


# ---------------------------------------------------------------------------
# MÓDULO 1C: ANÁLISIS DE SENTIMIENTO DE NOTICIAS
# ---------------------------------------------------------------------------

async def analyze_news_sentiments(news_items: list[dict]) -> list[dict]:
    """
    Recibe una lista de noticias, extrae los titulares y consulta al LLM
    para determinar el sentimiento (Alcista, Bajista, Neutral) en bloque.
    """
    if not news_items:
        return []

    # Construir el diccionario de titulares
    titulares_dict = {str(i): item["title"] for i, item in enumerate(news_items)}

    prompt = f"""
    Eres un analista financiero experto. Evalúa el sentimiento del mercado para los siguientes titulares de noticias.
    Determina si la noticia tiene un sentimiento "Alcista" (Bullish), "Bajista" (Bearish) o "Neutral" respecto a la materia prima o el mercado general.

    TITULARES:
    {json.dumps(titulares_dict, ensure_ascii=False, indent=2)}

    REGLAS DE RESPUESTA:
    - Responde ÚNICAMENTE con un objeto JSON válido.
    - El objeto JSON debe tener como claves los índices (ej. "0", "1", "2") y como valores el sentimiento asignado: "Alcista", "Bajista" o "Neutral".
    - No añadas explicaciones ni markdown.
    """

    try:
        respuesta_llm = await call_llm(prompt)
        sentimientos_json = json.loads(respuesta_llm)

        # Inyectar el sentimiento en la lista original
        for i, item in enumerate(news_items):
            item["sentiment"] = sentimientos_json.get(str(i), "Neutral")

    except Exception as e:
        print(f"[Insights Service] Error al analizar sentimiento de noticias: {e}")
        # Fallback de seguridad en caso de error
        for item in news_items:
            item["sentiment"] = "Neutral"

    return news_items
