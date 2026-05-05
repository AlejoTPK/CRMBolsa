import reflex as rx
from .state import AppState
from .components import sidebar, kpi_card, candlestick_chart, news_card, COLORS
from .insights_components import sovereign_insights_panel
from .insights_state import InsightsState

from .ai_recommendation_card import ai_recommendation_widget

def index() -> rx.Component:
    """The main Dashboard page layout."""
    
    return rx.hstack(
        # 1. Sidebar Space (Fixed)
        rx.box(
            sidebar(),
            position="fixed",
            left=0,
            top=0,
            height="100vh"
        ),
        
        # 2. Main Content Area (Scrollable)
        rx.box(
            rx.vstack(
                # Header Section
                rx.hstack(
                    rx.vstack(
                        rx.heading("Mercado en Tiempo Real", color=COLORS["text_main"], font_family="serif", size="8"),
                        rx.text("Monitor global de activos. Última actualización: Auto.", color=COLORS["text_muted"], size="2"),
                        align_items="start"
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("refresh-ccw", size=16),
                        "Refrescar Cotizaciones",
                        on_click=AppState.fetch_market_quotes,
                        is_loading=AppState.is_loading,
                        bg=COLORS["primary"],
                        color="#000",
                        _hover={"opacity": 0.8}
                    ),
                    width="100%",
                    align_items="center",
                    margin_bottom="2rem"
                ),
                
                # KPI Row (Hero Cards)
                rx.grid(
                    kpi_card("Oro (XAU/USD)", AppState.gold_price_fmt, AppState.gold_change_fmt, AppState.gold_is_positive, AppState.gold_status),
                    kpi_card("Petróleo Crudo (WTI)", AppState.oil_price_fmt, AppState.oil_change_fmt, AppState.oil_is_positive, AppState.oil_status),
                    columns="2",
                    spacing="6",
                    width="100%",
                    margin_bottom="3rem"
                ),
                
                # Charts Row — Gold & Oil side by side
                rx.grid(
                    rx.vstack(
                        candlestick_chart("ORO — XAU/USD", "XAU", AppState.gold_candlestick_fig, COLORS["primary"]),
                        ai_recommendation_widget("XAU"),
                        width="100%",
                        align_items="start"
                    ),
                    rx.vstack(
                        candlestick_chart("PETRÓLEO — WTI", "WTI", AppState.oil_candlestick_fig, "#B0C4DE"),
                        ai_recommendation_widget("WTI"),
                        width="100%",
                        align_items="start"
                    ),
                    columns="2",
                    spacing="6",
                    width="100%",
                    margin_bottom="2rem"
                ),
                
                # ── Sovereign Insights (IA) ──────────────────────────
                sovereign_insights_panel(),
                
                # Noticias Row
                rx.vstack(
                    rx.hstack(
                        rx.icon("newspaper", color=COLORS["primary"], size=18),
                        rx.text("Noticias de Impacto", color=COLORS["text_main"], font_family="serif", size="5", font_weight="bold"),
                        rx.spacer(),
                        rx.text("Fuente: Yahoo Finance · yfinance", color=COLORS["text_muted"], size="1"),
                        align_items="center",
                        width="100%",
                        margin_bottom="1rem"
                    ),
                    rx.grid(
                        rx.foreach(
                            AppState.news_items,
                            news_card
                        ),
                        columns="2",
                        spacing="4",
                        width="100%"
                    ),
                    align_items="start",
                    width="100%"
                ),
                
                width="100%",
                padding="3rem"
            ),
            
            # Content wrapper styles
            margin_left="250px",  # Offset for the fixed sidebar
            width="calc(100% - 250px)",
            min_height="100vh",
            bg=COLORS["background"]
        ),
        
        # Global Page styles
        bg=COLORS["background"],
        width="100%"
    )

app = rx.App(
    style={
        "font_family": "Manrope, system-ui, sans-serif",
        "background_color": COLORS["background"]
    }
)
app.add_page(
    index,
    title="Sovereign CRM | Dashboard",
    on_load=[AppState.fetch_market_quotes, AppState.listen_market_ws, InsightsState.fetch_latest_alert]
)
