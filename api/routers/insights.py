"""
Sovereign Insights — Router FastAPI
Archivo: api/routers/insights.py

Expone los endpoints para el motor de IA:
  GET  /insights/latest-alert    → Retorna la última alerta de anomalía
  POST /api/generate-daily-summary → Genera el resumen diario con el LLM
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional, List
from sqlalchemy import select

from api.models.insights import AlertaMercado, ResumenDiario, LeccionDelDia
from api.services.insights_service import (
    get_ultima_alerta,
    generar_resumen_diario,
)
from db.database import async_session
from db.models import DBAlertaMercado, DBResumenDiario

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
    ),
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
    ),
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
            ),
        )
    except ValueError as e:
        # Error de validación Pydantic (respuesta JSON del LLM mal formada)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"La respuesta del LLM no cumple el schema esperado: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al generar el resumen: {str(e)}",
        )


# ---------------------------------------------------------------------------
# ENDPOINTS DE HISTÓRICO: Consultar persistencia en PostgreSQL
# ---------------------------------------------------------------------------


@router.get(
    "/history/alerts",
    response_model=List[AlertaMercado],
    summary="Obtiene el historial de alertas de mercado",
)
async def get_alerts_history(limit: int = 50):
    """Retorna las últimas N alertas guardadas en la base de datos."""
    try:
        async with async_session() as session:
            query = (
                select(DBAlertaMercado)
                .order_by(DBAlertaMercado.timestamp.desc())
                .limit(limit)
            )
            result = await session.execute(query)
            db_alerts = result.scalars().all()

            return [
                AlertaMercado(
                    tipo_alerta=a.tipo_alerta,
                    titulo=a.titulo,
                    mensaje=a.mensaje,
                    nivel_severidad=a.nivel_severidad,
                )
                for a in db_alerts
            ]
    except Exception as e:
        print(f"[Insights Router] Error consultando historial de alertas: {e}")
        return []


@router.get(
    "/history/summaries",
    response_model=List[ResumenDiario],
    summary="Obtiene el historial de resúmenes diarios",
)
async def get_summaries_history(limit: int = 30):
    """Retorna los últimos N resúmenes diarios guardados en la base de datos."""
    try:
        async with async_session() as session:
            query = (
                select(DBResumenDiario)
                .order_by(DBResumenDiario.fecha_resumen.desc())
                .limit(limit)
            )
            result = await session.execute(query)
            db_summaries = result.scalars().all()

            return [
                ResumenDiario(
                    fecha_resumen=s.fecha_resumen.strftime("%Y-%m-%d"),
                    titulo_jornada=s.titulo_jornada,
                    resumen_oro=s.resumen_oro,
                    resumen_petroleo=s.resumen_petroleo,
                    leccion_del_dia=LeccionDelDia(
                        concepto=s.leccion_concepto, explicacion=s.leccion_explicacion
                    ),
                )
                for s in db_summaries
            ]
    except Exception as e:
        print(f"[Insights Router] Error consultando historial de resúmenes: {e}")
        return []


# ---------------------------------------------------------------------------
# ENDPOINT DE SEED: Generar datos de prueba para desarrollo
# ---------------------------------------------------------------------------


@router.post(
    "/seed-test-data",
    status_code=status.HTTP_201_CREATED,
    summary="Genera datos de prueba (alerta + resumen) para verificar el historial",
)
async def seed_test_data():
    """Inserta una alerta y un resumen de prueba directamente en la BD."""
    from api.services.insights_service import generar_resumen_diario

    resultados = []

    try:
        async with async_session() as session:
            db_alerta = DBAlertaMercado(
                tipo_alerta="XAU",
                titulo="[TEST] Oro sube por demanda de bancos centrales",
                mensaje="Esta es una alerta de prueba generada manualmente para verificar que el historial funciona. "
                "Los bancos centrales continúan acumulando reservas de oro como cobertura frente a la inflación.",
                nivel_severidad="INFORMATIVO",
            )
            session.add(db_alerta)
            await session.commit()
            resultados.append("alerta de prueba creada")
    except Exception as e:
        resultados.append(f"error creando alerta: {e}")

    try:
        resumen = await generar_resumen_diario()
        resultados.append(f"resumen diario generado para {resumen.fecha_resumen}")
    except Exception as e:
        resultados.append(f"error creando resumen: {e}")

    return {"status": "ok", "resultados": resultados}
