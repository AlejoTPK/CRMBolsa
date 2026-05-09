import asyncio
import json
import os
import websockets
from datetime import datetime

from dotenv import load_dotenv
from api.services.ws_manager import manager
from db.database import async_session
from db.models import MarketTick

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

# Símbolos a escuchar en Finnhub.
# Nota: Finnhub tiene símbolos específicos para commodities o criptos si no tienes el plan premium.
# Asumiremos símbolos genéricos como BINANCE:BTCUSDT (Bitcoin) o OANDA:XAU_USD (Oro) según tu plan.
SYMBOLS_TO_TRACK = ["OANDA:XAU_USD", "OANDA:WTICO_USD"]

async def process_finnhub_message(message: str):
    """
    Parsea el mensaje JSON de Finnhub, lo guarda en TimescaleDB y lo emite al frontend.
    Estructura esperada:
    {"data":[{"p":7296.89,"s":"BINANCE:BTCUSDT","t":1575526691134,"v":0.011467}], "type":"trade"}
    """
    try:
        data = json.loads(message)
        if data.get("type") == "trade":
            for trade in data.get("data", []):
                price = float(trade["p"])
                symbol = trade["s"]
                timestamp_ms = int(trade["t"])
                volume = float(trade["v"])

                # Convertir timestamp milisegundos a objeto datetime con tz
                dt_obj = datetime.fromtimestamp(timestamp_ms / 1000.0).astimezone()

                # 1. Guardar en PostgreSQL (TimescaleDB)
                try:
                    async with async_session() as session:
                        tick = MarketTick(
                            timestamp=dt_obj,
                            symbol=symbol,
                            price=price,
                            volume=volume
                        )
                        session.add(tick)
                        await session.commit()
                except Exception as db_e:
                    # Si el tick ya existe (IntegrityError de llave duplicada) lo ignoramos para no bloquear el flujo
                    pass

                # 2. Broadcast a los clientes de Reflex
                tick_payload = {
                    "symbol": symbol,
                    "price": price,
                    "volume": volume,
                    "timestamp": dt_obj.isoformat()
                }
                await manager.broadcast_tick(tick_payload)

    except Exception as e:
        print(f"[Finnhub Client] Error procesando mensaje: {e}")


async def finnhub_ws_client():
    """
    Mantiene una conexión persistente como cliente contra el WebSocket de Finnhub.
    """
    if not FINNHUB_API_KEY:
        print("[Finnhub Client] ⚠️ FINNHUB_API_KEY no configurada en .env. Saltando conexión.")
        return

    uri = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"
    
    while True:
        try:
            print(f"[Finnhub Client] Conectando a {uri}...")
            async with websockets.connect(uri) as websocket:
                # Suscribirse a los símbolos
                for symbol in SYMBOLS_TO_TRACK:
                    subscribe_msg = {"type": "subscribe", "symbol": symbol}
                    await websocket.send(json.dumps(subscribe_msg))
                    print(f"[Finnhub Client] Suscrito a {symbol}")

                # Loop de recepción de mensajes
                async for message in websocket:
                    await process_finnhub_message(message)
                    
        except websockets.ConnectionClosed:
            print("[Finnhub Client] Conexión cerrada. Reconectando en 5 segundos...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[Finnhub Client] Error de conexión: {e}. Reconectando en 5 segundos...")
            await asyncio.sleep(5)
