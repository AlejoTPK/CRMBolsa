import reflex as rx
import httpx
from typing import List
from .state import API_URL

class RecommendationsState(rx.State):
    """Estado para manejar las Recomendaciones de IA."""

    # --- Oro (XAU) ---
    xau_tendencia: str = ""
    xau_sugerencias: List[str] = []
    xau_disclaimer: str = ""
    xau_loaded: bool = False
    xau_loading: bool = False

    # --- Petróleo (WTI) ---
    wti_tendencia: str = ""
    wti_sugerencias: List[str] = []
    wti_disclaimer: str = ""
    wti_loaded: bool = False
    wti_loading: bool = False

    # Error global
    error_msg: str = ""

    async def generar_sugerencia(self, ticker: str):
        """Llama al backend de FastAPI para generar la sugerencia de IA."""
        ticker = ticker.upper()
        self.error_msg = ""

        # Marcar loading según ticker
        if ticker == "XAU":
            self.xau_loading = True
        else:
            self.wti_loading = True
        yield

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.get(f"{API_URL}/recommendations/{ticker}")
                if res.status_code == 200:
                    data = res.json()
                    if ticker == "XAU":
                        self.xau_tendencia = data.get("tendencia_corta", "")
                        self.xau_sugerencias = data.get("sugerencias_pedagogicas", [])
                        self.xau_disclaimer = data.get("disclaimer_obligatorio", "")
                        self.xau_loaded = True
                    else:
                        self.wti_tendencia = data.get("tendencia_corta", "")
                        self.wti_sugerencias = data.get("sugerencias_pedagogicas", [])
                        self.wti_disclaimer = data.get("disclaimer_obligatorio", "")
                        self.wti_loaded = True
                else:
                    self.error_msg = f"Error del servidor: {res.text}"
        except Exception as e:
            self.error_msg = f"Error de conexión: {str(e)}"

        if ticker == "XAU":
            self.xau_loading = False
        else:
            self.wti_loading = False
        yield
