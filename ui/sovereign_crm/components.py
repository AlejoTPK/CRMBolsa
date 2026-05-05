import reflex as rx

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

def kpi_card(title: str, price_str: str, change_str: str, is_positive: rx.Var[bool], status: str) -> rx.Component:
    """Dashboard KPI card showing real-time price and change."""
    
    # Conditional formatting based on price change
    trend_color = rx.cond(is_positive, COLORS["success"], COLORS["error"])
    trend_icon = rx.cond(is_positive, "trending-up", "trending-down")
    
    return glass_card(
        rx.vstack(
            rx.hstack(
                rx.text(title, color=COLORS["text_muted"], font_size="0.9rem", text_transform="uppercase", letter_spacing="1px"),
                rx.tooltip(
                    rx.icon("circle-help", size=14, color=COLORS["text_muted"]),
                    content=f"Cotización en tiempo real para {title}",
                    side="top"
                ),
                justify="between",
                width="100%"
            ),
            rx.text(
                price_str,
                color=COLORS["text_main"],
                font_size="2.5rem",
                font_family="serif",
                line_height="1.2"
            ),
            rx.hstack(
                rx.icon(trend_icon, color=trend_color, size=18),
                rx.text(
                    change_str,
                    color=trend_color,
                    font_weight="bold"
                ),
                rx.spacer(),
                rx.badge(
                    status,
                    color_scheme=rx.cond(status == "LIVE", "yellow", "gray"),
                    variant="surface"
                ),
                width="100%",
                align_items="center"
            ),
            spacing="3",
            align_items="start",
            width="100%"
        )
    )

def sidebar() -> rx.Component:
    """The minimalist navigation sidebar."""
    return rx.vstack(
        rx.heading("Sovereign", size="7", color=COLORS["primary"], font_family="serif", margin_bottom="2rem"),
        rx.vstack(
            rx.link(rx.hstack(rx.icon("layout-dashboard"), rx.text("Dashboard")), color=COLORS["text_main"], opacity=1.0),
            rx.link(rx.hstack(rx.icon("pie-chart"), rx.text("Portafolio")), color=COLORS["text_muted"], _hover={"color": COLORS["text_main"]}),
            rx.link(rx.hstack(rx.icon("newspaper"), rx.text("Noticias")), color=COLORS["text_muted"], _hover={"color": COLORS["text_main"]}),
            spacing="5",
            align_items="start",
            width="100%"
        ),
        rx.spacer(),
        rx.divider(border_color=COLORS["text_muted"], opacity=0.2),
        rx.hstack(
            rx.avatar(name="Inversor Beta", fallback="IB", bg=COLORS["primary_subtle"], color=COLORS["primary"]),
            rx.vstack(
                rx.text("Inversor Beta", color=COLORS["text_main"], font_weight="bold", size="2"),
                rx.text("Premium Tier", color=COLORS["primary"], size="1"),
                spacing="0",
                align_items="start"
            ),
            padding_top="1rem",
            align_items="center"
        ),
        bg=COLORS["surface"],
        padding="2rem",
        height="100vh",
        width="250px",
        border_right=f"1px solid {COLORS['text_muted']}25"
    )
OIL_COLOR = "#B0C4DE"   # Steel blue / silver

def candlestick_chart(title: str, symbol: str, fig: rx.Var, color: str) -> rx.Component:
    """Generic Candlestick chart component using Plotly natively in Reflex."""
    return rx.vstack(
        # Chart header with legend
        rx.hstack(
            rx.hstack(
                rx.box(width="12px", height="12px", bg=color, border_radius="3px"),
                rx.text(title, color=color, size="2", font_weight="bold", letter_spacing="1px"),
                align_items="center", spacing="2"
            ),
            rx.spacer(),
            rx.text("Tendencia 30 días", color=COLORS["text_muted"], size="1"),
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
