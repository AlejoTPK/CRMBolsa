import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from api.routers import market, insights, ws_router, recommendations
from api.services.insights_service import monitor_loop
from api.services.finnhub_client import finnhub_ws_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    - Al iniciar: lanza el monitor de anomalías en segundo plano.
    - Al cerrar: cancela la tarea limpiamente.
    """
    # STARTUP: lanzar el monitor cada 30 minutos y el cliente de Finnhub
    monitor_task = asyncio.create_task(monitor_loop())
    finnhub_task = asyncio.create_task(finnhub_ws_client())
    
    print("[Sovereign API] 🚀 Background task de anomalías iniciada.")
    print("[Sovereign API] 🚀 Cliente WebSocket de Finnhub iniciado.")
    yield
    # SHUTDOWN: cancelar las tareas
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
        "modules": ["market", "insights"]
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "db": "disconnected", "insights_monitor": "active"}
