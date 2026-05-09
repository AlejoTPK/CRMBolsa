import reflex as rx
from .state import AppState
from .components import navbar, kpi_card, candlestick_chart, news_card, COLORS
from .insights_components import quick_alert_card, combined_daily_summary_panel
from .insights_state import InsightsState

from .ai_recommendation_card import ai_recommendation_widget

def dashboard_view() -> rx.Component:
    return rx.vstack(
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
            kpi_card("Oro (XAU/USD)", AppState.gold_price_fmt, AppState.gold_change_fmt, AppState.gold_is_positive, AppState.gold_status, AppState.gold_sparkline_fig),
            kpi_card("Petróleo Crudo (WTI)", AppState.oil_price_fmt, AppState.oil_change_fmt, AppState.oil_is_positive, AppState.oil_status, AppState.oil_sparkline_fig),
            columns="2",
            spacing="6",
            width="100%",
            margin_bottom="1.5rem"
        ),
        
        # Alerta Rápida Global
        quick_alert_card(),
        rx.box(margin_bottom="1.5rem"),
        
        # Chart Controls (Global)
        rx.hstack(
            rx.segmented_control.root(
                rx.segmented_control.item("1D", value="1d"),
                rx.segmented_control.item("5D", value="5d"),
                rx.segmented_control.item("1M", value="1mo"),
                rx.segmented_control.item("6M", value="6mo"),
                rx.segmented_control.item("YTD", value="ytd"),
                rx.segmented_control.item("1A", value="1y"),
                rx.segmented_control.item("5A", value="5y"),
                rx.segmented_control.item("MAX", value="max"),
                value=AppState.global_time_period,
                on_change=AppState.change_time_period,
                variant="surface",
                color_scheme="gray",
                radius="full",
                size="2",
            ),
            rx.hstack(
                rx.text("Tipo de Gráfico:", color=COLORS["text_muted"], size="2", font_weight="bold"),
                rx.select(
                    ["Velas", "Barras", "Líneas"],
                    value=AppState.global_chart_type,
                    on_change=AppState.set_global_chart_type,
                    variant="surface",
                    color_scheme="gray",
                    radius="full",
                    size="2",
                    width="150px"
                ),
                align_items="center"
            ),
            width="100%",
            justify="between",
            align_items="center",
            margin_bottom="1rem"
        ),
        
        # Pestañas de Activos
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(rx.hstack(rx.icon("coins", size=16), rx.text("Oro (XAU/USD)")), value="oro"),
                rx.tabs.trigger(rx.hstack(rx.icon("droplet", size=16), rx.text("Petróleo (WTI)")), value="petroleo"),
                size="2",
                width="100%",
                margin_bottom="1.5rem"
            ),
            
            # ---- PESTAÑA: ORO ----
            rx.tabs.content(
                rx.vstack(
                    candlestick_chart("ORO — XAU/USD", "XAU", AppState.gold_candlestick_fig, COLORS["primary"]),
                    
                    rx.box(
                        ai_recommendation_widget("XAU"),
                        width="100%",
                        margin_bottom="1.5rem"
                    ),
                    
                    width="100%"
                ),
                value="oro"
            ),
            
            # ---- PESTAÑA: PETRÓLEO ----
            rx.tabs.content(
                rx.vstack(
                    candlestick_chart("PETRÓLEO — WTI", "WTI", AppState.oil_candlestick_fig, "#B0C4DE"),
                    
                    rx.box(
                        ai_recommendation_widget("WTI"),
                        width="100%",
                        margin_bottom="1.5rem"
                    ),
                    
                    width="100%"
                ),
                value="petroleo"
            ),
            
            default_value="oro",
            width="100%"
        ),
        
        width="100%",
        max_width="1400px",
        margin="0 auto",
        padding="2rem"
    )

def noticias_view() -> rx.Component:
    return rx.vstack(
        # Header Section
        rx.hstack(
            rx.vstack(
                rx.heading("Análisis & Noticias", color=COLORS["text_main"], font_family="serif", size="8"),
                rx.text("Reportes de inteligencia de mercado en tiempo real.", color=COLORS["text_muted"], size="2"),
                align_items="start"
            ),
            rx.spacer(),
            width="100%",
            align_items="center",
            margin_bottom="2rem"
        ),
        
        # Resumen Diario Unificado
        combined_daily_summary_panel(),
        
        # Noticias Generales de Mercado
        rx.vstack(
            rx.hstack(
                rx.icon("globe", color=COLORS["primary"], size=18),
                rx.text("Noticias de los Mercados", color=COLORS["text_main"], font_family="serif", size="5", font_weight="bold"),
                align_items="center",
                margin_bottom="1rem",
                width="100%"
            ),
            rx.grid(
                rx.foreach(AppState.news_items, news_card),
                columns="2",
                spacing="4",
                width="100%"
            ),
            width="100%"
        ),
        
        width="100%",
        max_width="1400px",
        margin="0 auto",
        padding="2rem"
    )

def portafolio_view() -> rx.Component:
    from .components import glass_card
    """The simulated portfolio view."""
    return rx.vstack(
        # Header with Total Balance and Donut Chart
        rx.hstack(
            rx.vstack(
                rx.text("Balance Total", color=COLORS["text_muted"], size="4", font_weight="bold"),
                rx.heading(AppState.portfolio_total_fmt, size="9", color=COLORS["primary"], font_family="serif"),
                align_items="start",
                spacing="2"
            ),
            rx.spacer(),
            rx.box(
                rx.plotly(data=AppState.portfolio_distribution_fig, height="250px", width="400px", config={"displayModeBar": False}),
                display="flex",
                justify_content="center",
                align_items="center"
            ),
            width="100%",
            align_items="center",
            margin_bottom="1rem"
        ),
        
        rx.divider(border_color=f"{COLORS['text_muted']}20", margin_y="1.5rem"),
        
        # Asset Breakdown
        rx.grid(
            glass_card(
                rx.vstack(
                    rx.hstack(
                        rx.box(width="12px", height="12px", bg="#D4AF37", border_radius="3px"),
                        rx.text("Oro Físico (XAU)", color=COLORS["text_main"], font_weight="bold"),
                        align_items="center", spacing="2"
                    ),
                    rx.hstack(
                        rx.text(f"{AppState.portfolio_gold_oz} oz", color=COLORS["text_muted"]),
                        rx.spacer(),
                        rx.text(AppState.portfolio_gold_fmt, color="#D4AF37", font_size="1.8rem", font_weight="bold", font_family="serif"),
                        width="100%",
                        align_items="baseline"
                    ),
                    align_items="start",
                    spacing="4"
                )
            ),
            glass_card(
                rx.vstack(
                    rx.hstack(
                        rx.box(width="12px", height="12px", bg="#B0C4DE", border_radius="3px"),
                        rx.text("Petróleo (WTI)", color=COLORS["text_main"], font_weight="bold"),
                        align_items="center", spacing="2"
                    ),
                    rx.hstack(
                        rx.text(f"{AppState.portfolio_oil_bbl} barriles", color=COLORS["text_muted"]),
                        rx.spacer(),
                        rx.text(AppState.portfolio_oil_fmt, color="#B0C4DE", font_size="1.8rem", font_weight="bold", font_family="serif"),
                        width="100%",
                        align_items="baseline"
                    ),
                    align_items="start",
                    spacing="4"
                )
            ),
            columns="2",
            spacing="5",
            width="100%"
        ),
        
        width="100%",
        max_width="1000px",
        margin="0 auto",
        padding="2rem"
    )

def index() -> rx.Component:
    """The main Dashboard page layout."""
    
    return rx.box(
        # Top Navbar
        navbar(),
        
        # Main Content Area switched by AppState.current_page
        rx.match(
            AppState.current_page,
            ("Dashboard", dashboard_view()),
            ("Portafolio", portafolio_view()),
            ("Noticias", noticias_view()),
            dashboard_view()
        ),
        
        # Global Page styles
        bg=COLORS["background"],
        min_height="100vh",
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
