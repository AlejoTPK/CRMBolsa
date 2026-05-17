import asyncio
import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from api.routers import market, insights, ws_router, recommendations
from api.services.insights_service import monitor_loop, generar_resumen_diario
from api.services.finnhub_client import finnhub_ws_client
from db.database import engine
from db.models import Base


async def _init_database():
    """Crea las tablas si no existen y genera resumen diario inicial."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[Sovereign API] ✅ Tablas de base de datos verificadas/creadas.")
    except Exception as e:
        print(f"[Sovereign API] ⚠️ No se pudieron verificar las tablas: {e}")
        return

    try:
        from sqlalchemy import select
        from db.models import DBResumenDiario
        from db.database import async_session

        hoy = datetime.date.today()
        async with async_session() as session:
            result = await session.execute(
                select(DBResumenDiario).where(DBResumenDiario.fecha_resumen == hoy)
            )
            existe = result.scalar_one_or_none()

        if not existe:
            print("[Sovereign API] 📝 Generando primer resumen diario...")
            await generar_resumen_diario()
        else:
            print(f"[Sovereign API] ✅ Ya existe resumen para hoy ({hoy}).")
    except Exception as e:
        print(f"[Sovereign API] ⚠️ No se pudo generar resumen inicial: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    - Al iniciar: crea tablas, lanza monitores, genera resumen inicial.
    - Al cerrar: cancela tareas limpiamente.
    """
    await _init_database()

    monitor_task = asyncio.create_task(monitor_loop())
    finnhub_task = asyncio.create_task(finnhub_ws_client())

    print("[Sovereign API] 🚀 Background task de anomalías iniciada.")
    print("[Sovereign API] 🚀 Cliente WebSocket de Finnhub iniciado.")
    yield
    monitor_task.cancel()
    finnhub_task.cancel()
    try:
        await monitor_task
        await finnhub_task
    except asyncio.CancelledError:
        print("[Sovereign API] 🛑 Background tasks detenidas.")


app = FastAPI(
    title="Sovereign CRM API",
    description="Financial CRM Backend for High-Net-Worth Investors — Sovereign Insights",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS for Reflex UI communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar la URL del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar Routers
app.include_router(market.router)
app.include_router(insights.router)
app.include_router(ws_router.router)
app.include_router(recommendations.router)


@app.get("/")
def read_root():
    return {
        "status": "Sovereign CRM API is running.",
        "version": "2.0.0",
        "modules": ["market", "insights"],
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "db": "disconnected", "insights_monitor": "active"}
