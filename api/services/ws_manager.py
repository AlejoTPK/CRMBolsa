import json
from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_tick(self, tick_data: dict):
        """
        Envía un tick de mercado (en formato JSON) a todas las conexiones activas.
        """
        message = json.dumps(tick_data)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

# Instancia global del manejador de WebSockets
manager = ConnectionManager()
