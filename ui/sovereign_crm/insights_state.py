"""
Sovereign Insights — Estado Reflex
Archivo: ui/sovereign_crm/insights_state.py

Gestiona la comunicación entre el frontend Reflex y los endpoints de FastAPI.
Se puede mezclar con AppState o usarse de forma independiente.
"""
import reflex as rx
import httpx
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
API_URL = os.getenv("API_URL", "http://127.0.0.1:8001")


class InsightsState(rx.State):
    """Estado para el motor Sovereign Insights."""

    # --- Última Alerta Rápida ---
    alerta_tipo: str = ""
    alerta_titulo: str = ""
    alerta_mensaje: str = ""
    alerta_severidad: str = ""          # "INFORMATIVO" | "MODERADO" | "CRITICO"
    hay_alerta: bool = False
    cargando_alerta: bool = False

    # --- Resumen Diario ---
    resumen_fecha: str = ""
    resumen_titulo: str = ""
    resumen_oro: str = ""
    resumen_petroleo: str = ""
    leccion_concepto: str = ""
    leccion_explicacion: str = ""
    hay_resumen: bool = False
    cargando_resumen: bool = False

    # --- Confirmación de verificación ---
    verificacion_msg: str = ""

    # --- Error global ---
    error_msg: str = ""

    # -----------------------------------------------------------------------
    # Vars computadas — Colores dinámicos según severidad de la alerta
    # -----------------------------------------------------------------------
    @rx.var
    def alerta_color(self) -> str:
        """Retorna el color de acento según el nivel de severidad."""
        mapa = {
            "INFORMATIVO": "#4ade80",   # Verde suave
            "MODERADO": "#facc15",       # Amarillo dorado
            "CRITICO": "#f87171",        # Rojo coral
        }
        return mapa.get(self.alerta_severidad, "#99907c")

    @rx.var
    def alerta_bg_color(self) -> str:
        """Retorna el color de fondo semitransparente de la alerta."""
        mapa = {
            "INFORMATIVO": "rgba(74, 222, 128, 0.08)",
            "MODERADO": "rgba(250, 204, 21, 0.08)",
            "CRITICO": "rgba(248, 113, 113, 0.12)",
        }
        return mapa.get(self.alerta_severidad, "rgba(153, 144, 124, 0.08)")

    @rx.var
    def alerta_icono(self) -> str:
        """Retorna el nombre del icono Lucide para la severidad."""
        mapa = {
            "INFORMATIVO": "info",
            "MODERADO": "triangle-alert",
            "CRITICO": "circle-x",
        }
        return mapa.get(self.alerta_severidad, "bell")

    # -----------------------------------------------------------------------
    # Acciones — Comunicación con FastAPI
    # -----------------------------------------------------------------------
    async def fetch_latest_alert(self):
        """
        Consulta GET /insights/latest-alert y actualiza el estado.
        Puedes llamar este método en el `on_load` de la página o en un intervalo.
        """
        self.cargando_alerta = True
        self.error_msg = ""
        self.verificacion_msg = ""
        yield

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                import datetime
                res = await client.get(f"{API_URL}/insights/latest-alert")

                if res.status_code == 200:
                    data = res.json()
                    ahora = datetime.datetime.now().strftime("%H:%M:%S")
                    if data is None:
                        # Sin alertas todavía
                        self.hay_alerta = False
                        self.verificacion_msg = f"✅ Verificación completada a las {ahora}. Sin anomalías detectadas en este momento."
                    else:
                        self.alerta_tipo = data.get("tipo_alerta", "")
                        self.alerta_titulo = data.get("titulo", "")
                        self.alerta_mensaje = data.get("mensaje", "")
                        self.alerta_severidad = data.get("nivel_severidad", "")
                        self.hay_alerta = True
                        self.verificacion_msg = f"✅ Verificación completada a las {ahora}. Se encontró 1 alerta activa."
                else:
                    self.error_msg = f"Error al consultar alertas: HTTP {res.status_code}"

        except Exception as e:
            self.error_msg = f"No se pudo conectar al backend: {e}"
        finally:
            self.cargando_alerta = False
            yield

    async def generate_daily_summary(self):
        """
        Llama a POST /insights/generate-daily-summary.
        Usualmente se dispara manualmente al cierre del mercado.
        """
        self.cargando_resumen = True
        self.error_msg = ""
        yield

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(f"{API_URL}/insights/generate-daily-summary")

                if res.status_code == 201:
                    data = res.json()
                    self.resumen_fecha = data.get("fecha_resumen", "")
                    self.resumen_titulo = data.get("titulo_jornada", "")
                    self.resumen_oro = data.get("resumen_oro", "")
                    self.resumen_petroleo = data.get("resumen_petroleo", "")
                    leccion = data.get("leccion_del_dia", {})
                    self.leccion_concepto = leccion.get("concepto", "")
                    self.leccion_explicacion = leccion.get("explicacion", "")
                    self.hay_resumen = True
                elif res.status_code == 503:
                    self.error_msg = "⚠️ El motor LLM no está configurado. Implementa call_llm()."
                else:
                    self.error_msg = f"Error del servidor: {res.status_code} — {res.text}"

        except Exception as e:
            self.error_msg = f"Error de conexión: {e}"
        finally:
            self.cargando_resumen = False
            yield
