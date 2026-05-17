import reflex as rx
import httpx
import os
from typing import Dict, Any
from dotenv import load_dotenv
import plotly.graph_objects as go

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8001")


class AppState(rx.State):
    """The central state for the Reflex UI."""

    # Data states
    gold_data: Dict[str, Any] = {
        "symbol": "XAU",
        "price": 0.0,
        "open_price": 0.0,
        "change": 0.0,
        "change_percent": 0.0,
        "status": "LOADING",
    }
    oil_data: Dict[str, Any] = {
        "symbol": "WTI",
        "price": 0.0,
        "open_price": 0.0,
        "change": 0.0,
        "change_percent": 0.0,
        "status": "LOADING",
    }
    gold_historical: list[Dict[str, Any]] = []
    oil_historical: list[Dict[str, Any]] = []
    news_items: list[Dict[str, Any]] = []

    # Portfolio Mock State
    portfolio_gold_oz: float = 15.5
    portfolio_oil_bbl: float = 500.0

    is_loading: bool = True
    global_chart_type: str = "Velas"
    global_time_period: str = "1mo"
    current_page: str = "Dashboard"

    def set_page(self, page: str):
        self.current_page = page

    def set_global_chart_type(self, chart_type: str):
        self.global_chart_type = chart_type

    def change_time_period(self, period: str | list[str]):
        if isinstance(period, list):
            self.global_time_period = period[0] if period else "1mo"
        else:
            self.global_time_period = period
        return AppState.fetch_market_quotes

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
    def portfolio_gold_value(self) -> float:
        return self.portfolio_gold_oz * self.gold_data.get("price", 0.0)

    @rx.var
    def portfolio_oil_value(self) -> float:
        return self.portfolio_oil_bbl * self.oil_data.get("price", 0.0)

    @rx.var
    def portfolio_total_value(self) -> float:
        return self.portfolio_gold_value + self.portfolio_oil_value

    @rx.var
    def portfolio_total_fmt(self) -> str:
        return f"${self.portfolio_total_value:,.2f}"

    @rx.var
    def portfolio_gold_fmt(self) -> str:
        return f"${self.portfolio_gold_value:,.2f}"

    @rx.var
    def portfolio_oil_fmt(self) -> str:
        return f"${self.portfolio_oil_value:,.2f}"

    @rx.var
    def portfolio_distribution_fig(self) -> go.Figure:
        labels = ["Oro Físico", "Petróleo WTI"]
        values = [self.portfolio_gold_value, self.portfolio_oil_value]

        if sum(values) == 0:
            fig = go.Figure()
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            return fig

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.8,
                    marker=dict(colors=["#D4AF37", "#B0C4DE"], line=dict(width=0)),
                    textinfo="none",
                    hovertemplate="<b>%{label}</b><br>%{percent}<br>$%{value:,.2f}<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                font=dict(size=12, color="#99907c"),
            ),
            margin=dict(t=10, b=10, l=10, r=80),
        )
        return fig

    def _create_sparkline(self, data_list, is_positive: bool) -> go.Figure:
        if not data_list:
            fig = go.Figure()
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=40,
                width=100,
            )
            return fig

        recent_data = data_list[-30:] if len(data_list) > 30 else data_list
        closes = [d["close"] for d in recent_data]

        if not closes:
            fig = go.Figure()
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=40,
                width=100,
            )
            return fig

        min_val = min(closes)
        max_val = max(closes)
        margin = (max_val - min_val) * 0.1 if max_val > min_val else min_val * 0.01

        color = "#4ade80" if is_positive else "#f87171"
        fillcolor = (
            "rgba(74, 222, 128, 0.1)" if is_positive else "rgba(248, 113, 113, 0.1)"
        )

        fig = go.Figure(
            data=[
                go.Scatter(
                    y=closes,
                    mode="lines",
                    line=dict(color=color, width=2),
                    fill="tozeroy",
                    fillcolor=fillcolor,
                    hoverinfo="skip",
                )
            ]
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False, range=[min_val - margin, max_val + margin]),
            showlegend=False,
            height=40,
            width=100,
        )
        return fig

    @rx.var
    def gold_sparkline_fig(self) -> go.Figure:
        is_pos = float(self.gold_data.get("change", 0.0)) >= 0
        return self._create_sparkline(self.gold_historical, is_pos)

    @rx.var
    def oil_sparkline_fig(self) -> go.Figure:
        is_pos = float(self.oil_data.get("change", 0.0)) >= 0
        return self._create_sparkline(self.oil_historical, is_pos)

    @rx.var
    def gold_candlestick_fig(self) -> go.Figure:
        if not self.gold_historical:
            return go.Figure()

        dates = [d["date"] for d in self.gold_historical]
        opens = [d["open"] for d in self.gold_historical]
        highs = [d["high"] for d in self.gold_historical]
        lows = [d["low"] for d in self.gold_historical]
        closes = [d["close"] for d in self.gold_historical]
        volumes = [d.get("volume", 0) for d in self.gold_historical]

        fig = go.Figure()

        if self.global_chart_type == "Líneas":
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=closes,
                    mode="lines",
                    line=dict(color="#D4AF37", width=2),
                    name="Precio",
                )
            )
        elif self.global_chart_type == "Barras":
            fig.add_trace(
                go.Ohlc(
                    x=dates,
                    open=opens,
                    high=highs,
                    low=lows,
                    close=closes,
                    line=dict(width=2.5),
                    name="Precio",
                )
            )
        else:
            fig.add_trace(
                go.Candlestick(
                    x=dates,
                    open=opens,
                    high=highs,
                    low=lows,
                    close=closes,
                    name="Precio",
                )
            )

        fig.add_trace(
            go.Bar(
                x=dates,
                y=volumes,
                marker_color="rgba(212, 175, 55, 0.3)",
                yaxis="y2",
                name="Volumen",
                showlegend=False,
            )
        )

        # Indicadores Técnicos
        sma20s = [d.get("sma20") for d in self.gold_historical]
        sma50s = [d.get("sma50") for d in self.gold_historical]
        bb_upper = [d.get("bb_upper") for d in self.gold_historical]
        bb_lower = [d.get("bb_lower") for d in self.gold_historical]

        # Bandas de Bollinger (Área sombreada)
        if any(v is not None for v in bb_lower):
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=bb_lower,
                    mode="lines",
                    line=dict(color="rgba(0,0,0,0)", width=0),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
        if any(v is not None for v in bb_upper):
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=bb_upper,
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(212, 175, 55, 0.05)",
                    line=dict(color="rgba(212, 175, 55, 0.2)", width=1, dash="dot"),
                    name="Banda Bollinger",
                )
            )

        # Medias Móviles
        if any(v is not None for v in sma20s):
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=sma20s,
                    mode="lines",
                    line=dict(color="rgba(255, 255, 255, 0.5)", width=1.5),
                    name="SMA 20",
                )
            )
        if any(v is not None for v in sma50s):
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=sma50s,
                    mode="lines",
                    line=dict(color="rgba(212, 175, 55, 0.6)", width=2),
                    name="SMA 50",
                )
            )

        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_rangeslider_visible=False,
            font=dict(color="#99907c"),
            hovermode="x unified",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10),
            ),
            yaxis=dict(gridcolor="rgba(212, 175, 55, 0.1)", domain=[0.3, 1.0]),
            yaxis2=dict(domain=[0.0, 0.2], showticklabels=False),
            xaxis=dict(
                gridcolor="rgba(212, 175, 55, 0.1)",
                type="category",
                nticks=6,
                showspikes=True,
                spikemode="across",
                spikethickness=1,
                spikedash="dot",
                spikecolor="#999",
            ),
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
        volumes = [d.get("volume", 0) for d in self.oil_historical]

        fig = go.Figure()

        if self.global_chart_type == "Líneas":
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=closes,
                    mode="lines",
                    line=dict(color="#B0C4DE", width=2),
                    name="Precio",
                )
            )
        elif self.global_chart_type == "Barras":
            fig.add_trace(
                go.Ohlc(
                    x=dates,
                    open=opens,
                    high=highs,
                    low=lows,
                    close=closes,
                    line=dict(width=2.5),
                    name="Precio",
                )
            )
        else:
            fig.add_trace(
                go.Candlestick(
                    x=dates,
                    open=opens,
                    high=highs,
                    low=lows,
                    close=closes,
                    name="Precio",
                )
            )

        fig.add_trace(
            go.Bar(
                x=dates,
                y=volumes,
                marker_color="rgba(176, 196, 222, 0.3)",
                yaxis="y2",
                name="Volumen",
                showlegend=False,
            )
        )

        # Indicadores Técnicos
        sma20s = [d.get("sma20") for d in self.oil_historical]
        sma50s = [d.get("sma50") for d in self.oil_historical]
        bb_upper = [d.get("bb_upper") for d in self.oil_historical]
        bb_lower = [d.get("bb_lower") for d in self.oil_historical]

        # Bandas de Bollinger (Área sombreada)
        if any(v is not None for v in bb_lower):
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=bb_lower,
                    mode="lines",
                    line=dict(color="rgba(0,0,0,0)", width=0),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
        if any(v is not None for v in bb_upper):
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=bb_upper,
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(176, 196, 222, 0.05)",
                    line=dict(color="rgba(176, 196, 222, 0.2)", width=1, dash="dot"),
                    name="Banda Bollinger",
                )
            )

        # Medias Móviles
        if any(v is not None for v in sma20s):
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=sma20s,
                    mode="lines",
                    line=dict(color="rgba(255, 255, 255, 0.5)", width=1.5),
                    name="SMA 20",
                )
            )
        if any(v is not None for v in sma50s):
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=sma50s,
                    mode="lines",
                    line=dict(color="rgba(176, 196, 222, 0.6)", width=2),
                    name="SMA 50",
                )
            )

        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_rangeslider_visible=False,
            font=dict(color="#99907c"),
            hovermode="x unified",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10),
            ),
            yaxis=dict(gridcolor="rgba(176, 196, 222, 0.1)", domain=[0.3, 1.0]),
            yaxis2=dict(domain=[0.0, 0.2], showticklabels=False),
            xaxis=dict(
                gridcolor="rgba(176, 196, 222, 0.1)",
                type="category",
                nticks=6,
                showspikes=True,
                spikemode="across",
                spikethickness=1,
                spikedash="dot",
                spikecolor="#999",
            ),
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
                gold_hist = await client.get(
                    f"{API_URL}/market/history/XAU?period={self.global_time_period}"
                )
                if gold_hist.status_code == 200:
                    self.gold_historical = gold_hist.json()

                # Oil history
                oil_hist = await client.get(
                    f"{API_URL}/market/history/WTI?period={self.global_time_period}"
                )
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

    async def fetch_news(self):
        """Solo refresca las noticias, sin recargar cotizaciones."""
        self.is_loading = True
        yield
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                news_res = await client.get(f"{API_URL}/market/news")
                if news_res.status_code == 200:
                    self.news_items = news_res.json()
        except Exception as e:
            print(f"Error fetching news: {e}")
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
                            message = await asyncio.wait_for(
                                websocket.recv(), timeout=0.5
                            )
                            data = json.loads(message)
                            # Se asume payload: {"symbol": "OANDA:XAU_USD", "price": ..., "volume": ...}
                            buffer[data["symbol"]] = data
                        except asyncio.TimeoutError:
                            pass  # Es normal, significa que no llegó tick en esos 500ms
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

                                    if "XAU" in symbol:
                                        # Usar open_price del día como referencia (viene del fetch HTTP)
                                        open_price = self.gold_data.get(
                                            "open_price", 0.0
                                        )
                                        if open_price and open_price > 0:
                                            change = price - open_price
                                            pct = (change / open_price) * 100
                                        else:
                                            # Fallback si no hay open_price: mantener los valores previos
                                            change = self.gold_data.get("change", 0.0)
                                            pct = self.gold_data.get(
                                                "change_percent", 0.0
                                            )
                                        self.gold_data.update(
                                            {
                                                "price": round(price, 2),
                                                "change": round(change, 2),
                                                "change_percent": round(pct, 2),
                                                "status": "LIVE",
                                            }
                                        )
                                    elif "WTI" in symbol or "CL=F" in symbol:
                                        # Usar open_price del día como referencia (viene del fetch HTTP)
                                        open_price = self.oil_data.get(
                                            "open_price", 0.0
                                        )
                                        if open_price and open_price > 0:
                                            change = price - open_price
                                            pct = (change / open_price) * 100
                                        else:
                                            # Fallback si no hay open_price: mantener los valores previos
                                            change = self.oil_data.get("change", 0.0)
                                            pct = self.oil_data.get(
                                                "change_percent", 0.0
                                            )
                                        self.oil_data.update(
                                            {
                                                "price": round(price, 2),
                                                "change": round(change, 2),
                                                "change_percent": round(pct, 2),
                                                "status": "LIVE",
                                            }
                                        )
                            # Limpiar buffer y reiniciar temporizador
                            buffer.clear()
                            last_flush = now

            except Exception as e:
                print(f"⚠️ Error conectando WS de Reflex: {e}")
                await asyncio.sleep(5)
