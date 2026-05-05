import reflex as rx
import httpx
import os
from typing import Dict, Any
from dotenv import load_dotenv
import plotly.graph_objects as go

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8001")

class AppState(rx.State):
    """The central state for the Reflex UI."""
    # Data states
    gold_data: Dict[str, Any] = {"symbol": "XAU", "price": 0.0, "change": 0.0, "change_percent": 0.0, "status": "LOADING"}
    oil_data: Dict[str, Any] = {"symbol": "WTI", "price": 0.0, "change": 0.0, "change_percent": 0.0, "status": "LOADING"}
    gold_historical: list[Dict[str, Any]] = []
    oil_historical: list[Dict[str, Any]] = []
    news_items: list[Dict[str, Any]] = []
    is_loading: bool = True
    
    @rx.var
    def gold_price_fmt(self) -> str:
        return f"${self.gold_data.get('price', 0.0):,.2f}"

    @rx.var
    def gold_change_fmt(self) -> str:
        return f"{self.gold_data.get('change', 0.0):,.2f} ({self.gold_data.get('change_percent', 0.0):.2f}%)"

    @rx.var
    def gold_is_positive(self) -> bool:
        return float(self.gold_data.get("change", 0.0)) >= 0

    @rx.var
    def gold_status(self) -> str:
        return self.gold_data.get("status", "LOADING")

    @rx.var
    def oil_price_fmt(self) -> str:
        return f"${self.oil_data.get('price', 0.0):,.2f}"

    @rx.var
    def oil_change_fmt(self) -> str:
        return f"{self.oil_data.get('change', 0.0):,.2f} ({self.oil_data.get('change_percent', 0.0):.2f}%)"

    @rx.var
    def oil_is_positive(self) -> bool:
        return float(self.oil_data.get("change", 0.0)) >= 0

    @rx.var
    def oil_status(self) -> str:
        return self.oil_data.get("status", "LOADING")
        
    @rx.var
    def gold_candlestick_fig(self) -> go.Figure:
        if not self.gold_historical:
            return go.Figure()
            
        dates = [d["date"] for d in self.gold_historical]
        opens = [d["open"] for d in self.gold_historical]
        highs = [d["high"] for d in self.gold_historical]
        lows = [d["low"] for d in self.gold_historical]
        closes = [d["close"] for d in self.gold_historical]
        
        fig = go.Figure(data=[go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes)])
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False,
            font=dict(color="#99907c"),
            yaxis=dict(gridcolor="rgba(212, 175, 55, 0.1)"),
            xaxis=dict(
                gridcolor="rgba(212, 175, 55, 0.1)",
                type='category',
                nticks=6
            )
        )
        return fig

    @rx.var
    def oil_candlestick_fig(self) -> go.Figure:
        if not self.oil_historical:
            return go.Figure()
            
        dates = [d["date"] for d in self.oil_historical]
        opens = [d["open"] for d in self.oil_historical]
        highs = [d["high"] for d in self.oil_historical]
        lows = [d["low"] for d in self.oil_historical]
        closes = [d["close"] for d in self.oil_historical]
        
        fig = go.Figure(data=[go.Candlestick(x=dates, open=opens, high=highs, low=lows, close=closes)])
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False,
            font=dict(color="#99907c"),
            yaxis=dict(gridcolor="rgba(176, 196, 222, 0.1)"),
            xaxis=dict(
                gridcolor="rgba(176, 196, 222, 0.1)",
                type='category',
                nticks=6
            )
        )
        return fig
    
    async def fetch_market_quotes(self):
        """Asynchronously queries the FastAPI backend for latest quotes and history."""
        self.is_loading = True
        yield
            
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Quotes
                res = await client.get(f"{API_URL}/market/quotes")
                if res.status_code == 200:
                    data = res.json()
                    self.gold_data = data.get("gold", self.gold_data)
                    self.oil_data = data.get("oil", self.oil_data)
                
                # Gold history
                gold_hist = await client.get(f"{API_URL}/market/history/XAU")
                if gold_hist.status_code == 200:
                    self.gold_historical = gold_hist.json()
                
                # Oil history
                oil_hist = await client.get(f"{API_URL}/market/history/WTI")
                if oil_hist.status_code == 200:
                    self.oil_historical = oil_hist.json()

                # Real news from yfinance
                news_res = await client.get(f"{API_URL}/market/news")
                if news_res.status_code == 200:
                    self.news_items = news_res.json()

        except Exception as e:
            print(f"Error connecting to backend: {e}")
            
        self.is_loading = False
        yield

    @rx.event(background=True)
    async def listen_market_ws(self):
        """
        Mantiene una conexión WebSocket al backend y agrupa (throttling) las actualizaciones 
        cada 1.5s para no sobrecargar el estado de Reflex.
        """
        import asyncio
        import websockets
        import json
        import time

        ws_url = f"{API_URL.replace('http', 'ws')}/ws/market"
        
        while True:
            try:
                async with websockets.connect(ws_url) as websocket:
                    print(f"✅ Reflex WebSocket conectado a {ws_url}")
                    
                    buffer = {}
                    last_flush = time.time()
                    
                    while True:
                        try:
                            # Esperar mensaje con un pequeño timeout
                            message = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                            data = json.loads(message)
                            # Se asume payload: {"symbol": "OANDA:XAU_USD", "price": ..., "volume": ...}
                            buffer[data["symbol"]] = data
                        except asyncio.TimeoutError:
                            pass # Es normal, significa que no llegó tick en esos 500ms
                        except websockets.ConnectionClosed:
                            print("❌ Conexión WebSocket cerrada, reconectando...")
                            break
                        
                        # Patrón de Throttling: Procesar el buffer cada 1.5 segundos
                        now = time.time()
                        if now - last_flush >= 1.5 and buffer:
                            # Entramos en un contexto Reactivo para aplicar cambios a la UI en lote
                            async with self:
                                for symbol, data in buffer.items():
                                    price = data["price"]
                                    
                                    # Lógica simple para actualizar Oro o Petróleo
                                    if "XAU" in symbol:
                                        # Fake calculation of change for visual effect
                                        change = price - self.gold_data.get("price", price)
                                        pct = (change / self.gold_data.get("price", 1)) * 100
                                        self.gold_data.update({
                                            "price": price, 
                                            "change": self.gold_data.get("change", 0) + change,
                                            "change_percent": pct,
                                            "status": "LIVE"
                                        })
                                    elif "WTI" in symbol or "CL=F" in symbol:
                                        change = price - self.oil_data.get("price", price)
                                        pct = (change / self.oil_data.get("price", 1)) * 100
                                        self.oil_data.update({
                                            "price": price, 
                                            "change": self.oil_data.get("change", 0) + change,
                                            "change_percent": pct,
                                            "status": "LIVE"
                                        })
                            # Limpiar buffer y reiniciar temporizador
                            buffer.clear()
                            last_flush = now
                            
            except Exception as e:
                print(f"⚠️ Error conectando WS de Reflex: {e}")
                await asyncio.sleep(5)
