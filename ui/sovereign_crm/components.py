import reflex as rx
import plotly.graph_objects as go
# Obsidian Sovereign Design Tokens
COLORS = {
    "background": "#121317",
    "surface": "#1a1b20",
    "surface_high": "#292a2e",
    "primary": "#D4AF37",      # Gold
    "primary_glow": "rgba(212, 175, 55, 0.4)",
    "primary_subtle": "rgba(212, 175, 55, 0.1)",
    "text_main": "#e3e2e8",
    "text_muted": "#99907c",
    "success": "#D4AF37",      # Using gold for success per design rules
    "error": "#ffb4ab",
}

def glass_card(*children, **kwargs) -> rx.Component:
    """A glassmorphic container for dashboard widgets."""
    default_style = {
        "bg": COLORS["surface"],
        "border_radius": "12px",
        "padding": "1.5rem",
        "box_shadow": f"0 24px 48px rgba(0,0,0,0.4)",
        "border": f"1px solid {COLORS['text_muted']}25",  # 15% opacity ghost border
        "width": "100%",
        "transition": "all 0.3s ease",
        "_hover": {
            "bg": COLORS["surface_high"],
            "box_shadow": f"0 24px 48px {COLORS['primary_glow']}",
        }
    }
    # Update defaults with any passed styles
    if "style" in kwargs:
        default_style.update(kwargs.pop("style"))
        
    return rx.box(
        *children,
        style=default_style,
        **kwargs
    )

def kpi_card(title: str, price_str: str, change_str: str, is_positive: rx.Var[bool], status: str, sparkline_fig: rx.Var[go.Figure]) -> rx.Component:
    """Dashboard KPI card showing real-time price, change, and sparkline."""
    
    # Conditional formatting based on price change
    trend_color = rx.cond(is_positive, COLORS["success"], COLORS["error"])
    
    return glass_card(
        rx.hstack(
            # Left side: Text data
            rx.vstack(
                rx.text(title, color=COLORS["text_muted"], font_size="1.1rem", font_weight="bold"),
                rx.text(
                    price_str,
                    color=COLORS["text_main"],
                    font_size="2.2rem",
                    font_weight="bold",
                    line_height="1.2"
                ),
                rx.text(
                    change_str,
                    color=trend_color,
                    font_weight="bold",
                    font_size="1rem"
                ),
                spacing="1",
                align_items="start",
            ),
            rx.spacer(),
            # Right side: Sparkline
            rx.box(
                rx.plotly(data=sparkline_fig, height="40px", width="100px", config={"displayModeBar": False}),
                display="flex",
                align_items="end",
                justify_content="flex-end"
            ),
            width="100%",
            align_items="center"
        ),
        padding="1rem 1.5rem"
    )

def navbar() -> rx.Component:
    from .state import AppState
    """The main navigation top bar."""
    return rx.hstack(
        rx.hstack(
            rx.heading("Sovereign", size="6", color=COLORS["primary"], font_family="serif"),
            rx.spacer(),
            rx.hstack(
                rx.link(rx.hstack(rx.icon("layout-dashboard"), rx.text("Dashboard")), 
                        color=rx.cond(AppState.current_page == "Dashboard", COLORS["text_main"], COLORS["text_muted"]), 
                        on_click=AppState.set_page("Dashboard"), cursor="pointer", _hover={"color": COLORS["text_main"]}),
                rx.link(rx.hstack(rx.icon("pie-chart"), rx.text("Portafolio")), 
                        color=rx.cond(AppState.current_page == "Portafolio", COLORS["text_main"], COLORS["text_muted"]), 
                        on_click=AppState.set_page("Portafolio"), cursor="pointer", _hover={"color": COLORS["text_main"]}),
                rx.link(rx.hstack(rx.icon("newspaper"), rx.text("Noticias & Análisis")), 
                        color=rx.cond(AppState.current_page == "Noticias", COLORS["text_main"], COLORS["text_muted"]), 
                        on_click=AppState.set_page("Noticias"), cursor="pointer", _hover={"color": COLORS["text_main"]}),
                spacing="5",
                align_items="center"
            ),
            rx.spacer(),
            rx.hstack(
                rx.avatar(name="Inversor Beta", fallback="IB", bg=COLORS["primary_subtle"], color=COLORS["primary"], size="2"),
                rx.vstack(
                    rx.text("Inversor Beta", color=COLORS["text_main"], font_weight="bold", size="2"),
                    rx.text("Premium Tier", color=COLORS["primary"], size="1"),
                    spacing="0",
                    align_items="start"
                ),
                align_items="center",
                spacing="3"
            ),
            width="100%",
            max_width="1400px",
            margin="0 auto",
            align_items="center"
        ),
        bg=COLORS["surface"],
        padding="1rem 2rem",
        width="100%",
        border_bottom=f"1px solid {COLORS['text_muted']}25",
        position="sticky",
        top="0",
        z_index="999"
    )
OIL_COLOR = "#B0C4DE"   # Steel blue / silver

def candlestick_chart(title: str, symbol: str, fig: rx.Var, color: str) -> rx.Component:
    """Generic Candlestick chart component using Plotly natively in Reflex."""
    from .state import AppState
    return rx.vstack(
        # Chart header with legend
        rx.hstack(
            rx.hstack(
                rx.box(width="12px", height="12px", bg=color, border_radius="3px"),
                rx.text(title, color=color, size="2", font_weight="bold", letter_spacing="1px"),
                align_items="center", spacing="2"
            ),
            rx.spacer(),
            rx.hstack(
                rx.button("1D", size="1", variant=rx.cond(AppState.global_time_period == "1d", "solid", "soft"), color_scheme="gray", on_click=AppState.change_time_period("1d"), cursor="pointer"),
                rx.button("1W", size="1", variant=rx.cond(AppState.global_time_period == "5d", "solid", "soft"), color_scheme="gray", on_click=AppState.change_time_period("5d"), cursor="pointer"),
                rx.button("1M", size="1", variant=rx.cond(AppState.global_time_period == "1mo", "solid", "soft"), color_scheme="gray", on_click=AppState.change_time_period("1mo"), cursor="pointer"),
                rx.button("3M", size="1", variant=rx.cond(AppState.global_time_period == "3mo", "solid", "soft"), color_scheme="gray", on_click=AppState.change_time_period("3mo"), cursor="pointer"),
                rx.button("1Y", size="1", variant=rx.cond(AppState.global_time_period == "1y", "solid", "soft"), color_scheme="gray", on_click=AppState.change_time_period("1y"), cursor="pointer"),
                spacing="1",
                bg=COLORS["surface_high"],
                padding="0.25rem",
                border_radius="6px",
                border=f"1px solid {COLORS['text_muted']}25"
            ),
            width="100%",
            align_items="center",
            margin_bottom="0.75rem"
        ),
        # Chart box rendering Plotly
        rx.box(
            rx.plotly(data=fig, height="320px", width="100%", config={"displayModeBar": False}),
            width="100%",
            bg=COLORS["surface"],
            border_radius="12px",
            padding="1.25rem",
            border=f"1px solid {color}30",
            overflow="hidden"
        ),
        width="100%",
        align_items="start",
        spacing="0"
    )

def news_card(item: rx.Var[dict]) -> rx.Component:
    """Premium news card — Var-compatible for rx.foreach."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    item["asset"],
                    color_scheme=rx.cond(item["asset"] == "Oro", "yellow", "blue"),
                    variant="surface",
                    size="1"
                ),
                rx.spacer(),
                rx.text(item["publisher"], color=COLORS["text_muted"], size="1"),
                width="100%",
                align_items="center"
            ),
            rx.link(
                item["title"],
                href=item["url"],
                is_external=True,
                color=COLORS["text_main"],
                font_weight="600",
                font_size="0.9rem",
                line_height="1.4",
                _hover={"color": COLORS["primary"], "text_decoration": "none"}
            ),
            rx.text(
                item["url"],
                color=COLORS["text_muted"],
                size="1",
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
                max_width="100%"
            ),
            spacing="2",
            align_items="start",
            width="100%"
        ),
        padding="1rem",
        bg=COLORS["surface_high"],
        border_radius="10px",
        border_left=rx.cond(item["asset"] == "Oro", f"3px solid {COLORS['primary']}", "3px solid #B0C4DE"),
        width="100%",
        transition="all 0.2s ease",
        _hover={"bg": "#333438"}
    )
