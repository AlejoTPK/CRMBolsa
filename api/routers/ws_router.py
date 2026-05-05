from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.services.ws_manager import manager

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws/market")
async def market_websocket_endpoint(websocket: WebSocket):
    """
    Endpoint al que se conectará Reflex para recibir los datos de mercado en tiempo real.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Mantener la conexión abierta; no esperamos recibir datos del cliente
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
