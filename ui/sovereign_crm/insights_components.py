"""
Sovereign Insights — Componentes Reflex
Archivo: ui/sovereign_crm/insights_components.py

Exports:
  sovereign_insights_panel()  → Panel completo de Insights (alerta + resumen diario)
  quick_alert_card()          → Solo la tarjeta de alerta (para usar en el header)
"""
import reflex as rx
from .insights_state import InsightsState

# Reutilizamos los tokens de color del proyecto
COLORS = {
    "background": "#121317",
    "surface": "#1a1b20",
    "surface_high": "#292a2e",
    "primary": "#D4AF37",
    "primary_glow": "rgba(212, 175, 55, 0.4)",
    "primary_subtle": "rgba(212, 175, 55, 0.1)",
    "text_main": "#e3e2e8",
    "text_muted": "#99907c",
}


# ---------------------------------------------------------------------------
# COMPONENTE 1: Tarjeta de Alerta Rápida
# ---------------------------------------------------------------------------

def _estado_sin_alerta() -> rx.Component:
    """Estado vacío cuando no hay alertas activas."""
    return rx.center(
        rx.vstack(
            rx.icon("shield-check", size=32, color=COLORS["text_muted"]),
            rx.text(
                "Sin anomalías detectadas",
                color=COLORS["text_muted"],
                size="2",
                font_weight="500",
            ),
            rx.text(
                "El monitor revisa los mercados cada 30 minutos",
                color=COLORS["text_muted"],
                size="1",
                opacity="0.6",
            ),
            spacing="2",
            align="center",
        ),
        padding="2rem",
        width="100%",
    )


def quick_alert_card() -> rx.Component:
    """
    Tarjeta de Alerta Rápida con color dinámico según severidad.
    Muestra: icono, título, mensaje y badge de severidad.
    """
    return rx.box(
        rx.vstack(
            # Header de la sección
            rx.hstack(
                rx.hstack(
                    rx.icon("zap", size=16, color=COLORS["primary"]),
                    rx.text(
                        "ALERTA RÁPIDA",
                        color=COLORS["primary"],
                        size="1",
                        font_weight="700",
                        letter_spacing="2px",
                    ),
                    align_items="center",
                    spacing="2",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("refresh-ccw", size=12),
                    "Verificar",
                    on_click=InsightsState.fetch_latest_alert,
                    is_loading=InsightsState.cargando_alerta,
                    size="1",
                    variant="ghost",
                    color=COLORS["text_muted"],
                    _hover={"color": COLORS["text_main"]},
                ),
                width="100%",
                align_items="center",
                margin_bottom="1rem",
            ),

            # Contenido condicional: alerta activa o estado vacío
            rx.cond(
                InsightsState.hay_alerta,

                # --- ALERTA ACTIVA ---
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon(
                                InsightsState.alerta_icono,
                                size=20,
                                color=InsightsState.alerta_color,
                            ),
                            rx.text(
                                InsightsState.alerta_titulo,
                                color=COLORS["text_main"],
                                font_weight="700",
                                size="3",
                                line_height="1.3",
                            ),
                            align_items="start",
                            spacing="3",
                            width="100%",
                        ),
                        rx.text(
                            InsightsState.alerta_mensaje,
                            color=COLORS["text_muted"],
                            size="2",
                            line_height="1.6",
                        ),
                        rx.hstack(
                            rx.badge(
                                InsightsState.alerta_tipo,
                                variant="surface",
                                color_scheme="yellow",
                                size="1",
                            ),
                            rx.badge(
                                InsightsState.alerta_severidad,
                                variant="solid",
                                size="1",
                                style={"background": InsightsState.alerta_color, "color": "#000"},
                            ),
                            spacing="2",
                        ),
                        spacing="3",
                        align_items="start",
                        width="100%",
                    ),
                    padding="1.25rem",
                    border_radius="10px",
                    border_left=rx.Var.create(
                        f"3px solid {InsightsState.alerta_color}"
                    ),
                    bg=InsightsState.alerta_bg_color,
                    width="100%",
                    transition="all 0.3s ease",
                ),

                # --- SIN ALERTAS ---
                _estado_sin_alerta(),
            ),

            # Mensaje de confirmación post-verificación
            rx.cond(
                InsightsState.verificacion_msg != "",
                rx.hstack(
                    rx.icon("shield-check", size=14, color="#4ade80"),
                    rx.text(
                        InsightsState.verificacion_msg,
                        color="#4ade80",
                        size="1",
                        font_weight="500",
                    ),
                    align_items="center",
                    spacing="2",
                    margin_top="0.75rem",
                    padding="0.5rem 0.75rem",
                    background="rgba(74, 222, 128, 0.08)",
                    border_radius="6px",
                    border_left="3px solid #4ade80",
                ),
                rx.box(),
            ),

            # Mensaje de error si falla la conexión
            rx.cond(
                InsightsState.error_msg != "",
                rx.callout(
                    InsightsState.error_msg,
                    icon="triangle-alert",
                    color_scheme="red",
                    size="1",
                    width="100%",
                ),
                rx.box(),
            ),

            spacing="0",
            align_items="start",
            width="100%",
        ),
        bg=COLORS["surface"],
        border_radius="12px",
        padding="1.5rem",
        border=f"1px solid {COLORS['text_muted']}20",
        box_shadow="0 8px 24px rgba(0,0,0,0.3)",
        width="100%",
        _hover={
            "bg": COLORS["surface_high"],
            "box_shadow": "0 8px 24px rgba(212,175,55,0.15)",
        },
        transition="all 0.3s ease",
    )


# ---------------------------------------------------------------------------
# COMPONENTE 2: Panel de Resumen Diario
# ---------------------------------------------------------------------------

def _leccion_card() -> rx.Component:
    """Tarjeta especial para la Lección del Día."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("graduation-cap", size=16, color=COLORS["primary"]),
                rx.text(
                    "LECCIÓN DEL DÍA",
                    color=COLORS["primary"],
                    size="1",
                    font_weight="700",
                    letter_spacing="2px",
                ),
                spacing="2",
                align_items="center",
            ),
            rx.text(
                InsightsState.leccion_concepto,
                color=COLORS["text_main"],
                font_weight="700",
                size="4",
                font_family="serif",
            ),
            rx.text(
                InsightsState.leccion_explicacion,
                color=COLORS["text_muted"],
                size="2",
                line_height="1.7",
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        padding="1.5rem",
        border_radius="12px",
        bg=COLORS["primary_subtle"],
        border=f"1px solid {COLORS['primary']}40",
        width="100%",
    )


def daily_summary_panel() -> rx.Component:
    """
    Panel completo del Resumen Diario.
    Incluye: Título, Resumen de Oro, Resumen de Petróleo y Lección del Día.
    """
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.hstack(
                    rx.icon("book-open", size=16, color=COLORS["primary"]),
                    rx.text(
                        "RESUMEN DIARIO",
                        color=COLORS["primary"],
                        size="1",
                        font_weight="700",
                        letter_spacing="2px",
                    ),
                    align_items="center",
                    spacing="2",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("brain", size=12),
                    "Generar con IA",
                    on_click=InsightsState.generate_daily_summary,
                    is_loading=InsightsState.cargando_resumen,
                    size="1",
                    bg=COLORS["primary"],
                    color="#000",
                    font_weight="700",
                    _hover={"opacity": "0.85"},
                ),
                width="100%",
                align_items="center",
                margin_bottom="1rem",
            ),

            # Contenido condicional: resumen activo o estado vacío
            rx.cond(
                InsightsState.hay_resumen,

                # --- RESUMEN ACTIVO ---
                rx.vstack(
                    # Fecha y Título
                    rx.vstack(
                        rx.text(
                            InsightsState.resumen_fecha,
                            color=COLORS["text_muted"],
                            size="1",
                            font_weight="500",
                            letter_spacing="1px",
                            text_transform="uppercase",
                        ),
                        rx.heading(
                            InsightsState.resumen_titulo,
                            size="6",
                            color=COLORS["text_main"],
                            font_family="serif",
                            line_height="1.3",
                        ),
                        spacing="1",
                        align_items="start",
                        width="100%",
                        margin_bottom="0.5rem",
                    ),

                    # Grid Oro / Petróleo
                    rx.grid(
                        # Resumen Oro
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.box(
                                        width="10px",
                                        height="10px",
                                        bg=COLORS["primary"],
                                        border_radius="3px",
                                    ),
                                    rx.text(
                                        "ORO — XAU/USD",
                                        color=COLORS["primary"],
                                        size="1",
                                        font_weight="700",
                                        letter_spacing="1px",
                                    ),
                                    align_items="center",
                                    spacing="2",
                                ),
                                rx.text(
                                    InsightsState.resumen_oro,
                                    color=COLORS["text_muted"],
                                    size="2",
                                    line_height="1.6",
                                ),
                                spacing="2",
                                align_items="start",
                            ),
                            padding="1rem",
                            bg=COLORS["surface_high"],
                            border_radius="10px",
                            border_left=f"3px solid {COLORS['primary']}",
                        ),

                        # Resumen Petróleo
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.box(
                                        width="10px",
                                        height="10px",
                                        bg="#B0C4DE",
                                        border_radius="3px",
                                    ),
                                    rx.text(
                                        "PETRÓLEO — WTI",
                                        color="#B0C4DE",
                                        size="1",
                                        font_weight="700",
                                        letter_spacing="1px",
                                    ),
                                    align_items="center",
                                    spacing="2",
                                ),
                                rx.text(
                                    InsightsState.resumen_petroleo,
                                    color=COLORS["text_muted"],
                                    size="2",
                                    line_height="1.6",
                                ),
                                spacing="2",
                                align_items="start",
                            ),
                            padding="1rem",
                            bg=COLORS["surface_high"],
                            border_radius="10px",
                            border_left="3px solid #B0C4DE",
                        ),

                        columns="2",
                        spacing="4",
                        width="100%",
                    ),

                    # Lección del Día
                    _leccion_card(),

                    spacing="4",
                    align_items="start",
                    width="100%",
                ),

                # --- SIN RESUMEN ---
                rx.center(
                    rx.vstack(
                        rx.icon("calendar-days", size=32, color=COLORS["text_muted"]),
                        rx.text(
                            "Aún no hay resumen para hoy",
                            color=COLORS["text_muted"],
                            size="2",
                            font_weight="500",
                        ),
                        rx.text(
                            "Presiona 'Generar con IA' al cierre del mercado (4PM ET)",
                            color=COLORS["text_muted"],
                            size="1",
                            opacity="0.6",
                            text_align="center",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    padding="2.5rem",
                ),
            ),

            # Error
            rx.cond(
                InsightsState.error_msg != "",
                rx.callout(
                    InsightsState.error_msg,
                    icon="triangle-alert",
                    color_scheme="red",
                    size="1",
                    width="100%",
                ),
                rx.box(),
            ),

            spacing="0",
            align_items="start",
            width="100%",
        ),
        bg=COLORS["surface"],
        border_radius="12px",
        padding="1.5rem",
        border=f"1px solid {COLORS['text_muted']}20",
        box_shadow="0 8px 24px rgba(0,0,0,0.3)",
        width="100%",
    )


# ---------------------------------------------------------------------------
# COMPONENTE MAESTRO: Panel Completo de Sovereign Insights
# ---------------------------------------------------------------------------

def sovereign_insights_panel() -> rx.Component:
    """
    Componente completo de Sovereign Insights.
    Combina la alerta rápida y el resumen diario en un layout vertical.
    
    Uso en sovereign_crm.py:
        from .insights_components import sovereign_insights_panel
        # ... dentro del layout principal:
        sovereign_insights_panel()
    """
    return rx.vstack(
        # Título de la sección
        rx.hstack(
            rx.icon("sparkles", size=20, color=COLORS["primary"]),
            rx.heading(
                "Sovereign Insights",
                size="6",
                color=COLORS["text_main"],
                font_family="serif",
            ),
            rx.badge("BETA", color_scheme="yellow", variant="surface", size="1"),
            align_items="center",
            spacing="3",
            margin_bottom="1.5rem",
        ),

        # Tarjeta de Alerta Rápida
        quick_alert_card(),

        # Panel de Resumen Diario
        daily_summary_panel(),

        spacing="4",
        align_items="start",
        width="100%",
    )
