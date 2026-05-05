"""
Sovereign Insights — Router FastAPI
Archivo: api/routers/insights.py

Expone los endpoints para el motor de IA:
  GET  /insights/latest-alert    → Retorna la última alerta de anomalía
  POST /api/generate-daily-summary → Genera el resumen diario con el LLM
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional

from api.models.insights import AlertaMercado, ResumenDiario
from api.services.insights_service import (
    get_ultima_alerta,
    generar_resumen_diario,
)

router = APIRouter(
    prefix="/insights",
    tags=["Sovereign Insights — IA"],
)


# ---------------------------------------------------------------------------
# ENDPOINT 1: Última Alerta Rápida (consultada por el frontend en polling)
# ---------------------------------------------------------------------------
@router.get(
    "/latest-alert",
    response_model=Optional[AlertaMercado],
    summary="Obtiene la última alerta de anomalía de mercado",
    description=(
        "Retorna la última `AlertaMercado` generada por el monitor en segundo plano. "
        "Si no hay alertas aún, retorna `null`. El frontend debe hacer polling a este "
        "endpoint cada 1-2 minutos para mostrar alertas en tiempo casi-real."
    )
)
async def get_latest_alert():
    """
    Retorna la última alerta cacheada en memoria.
    En producción, esto consultaría la tabla 'alertas' de Supabase.
    """
    alerta = get_ultima_alerta()
    return alerta  # None es válido (frontend maneja el estado vacío)


# ---------------------------------------------------------------------------
# ENDPOINT 2: Resumen Diario — llamar al cierre del mercado (4PM ET)
# ---------------------------------------------------------------------------
@router.post(
    "/generate-daily-summary",
    response_model=ResumenDiario,
    status_code=status.HTTP_201_CREATED,
    summary="Genera el Resumen Diario de mercado con IA",
    description=(
        "Recopila datos reales de yfinance (OHLCV de XAU y WTI), construye un prompt "
        "contextualizado, llama al LLM y retorna un `ResumenDiario` validado por Pydantic. "
        "Llamar este endpoint al cierre del mercado (ej. mediante un cron job)."
    )
)
async def generate_daily_summary():
    """
    Orquesta la generación del Resumen Diario.
    Lanza un 503 si el LLM no está configurado aún (call_llm no implementado).
    Lanza un 422 si la respuesta del LLM no cumple el schema Pydantic.
    """
    try:
        resumen = await generar_resumen_diario()
        return resumen

    except NotImplementedError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"El motor LLM no está configurado: {str(e)}. "
                "Implementa la función `call_llm()` en api/services/insights_service.py."
            )
        )
    except ValueError as e:
        # Error de validación Pydantic (respuesta JSON del LLM mal formada)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"La respuesta del LLM no cumple el schema esperado: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al generar el resumen: {str(e)}"
        )
