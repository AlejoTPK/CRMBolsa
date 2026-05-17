import reflex as rx
from .recommendations_state import RecommendationsState

# --------------------------------------------------------------------------
# Componentes de sugerencia individuales para cada ticker (tipado explícito)
# --------------------------------------------------------------------------


def _sugerencia_item(sugerencia: rx.Var) -> rx.Component:
    """Renderiza una sola sugerencia con ícono."""
    return rx.hstack(
        rx.icon(tag="circle-check-big", size=14, color="#D4AF37"),
        rx.text(
            sugerencia,
            font_size="0.95rem",
            color="#e5e7eb",
            line_height="1.5",
        ),
        align_items="start",
        spacing="2",
    )


def _chat_bubble(
    tendencia: rx.Var, sugerencias: rx.Var, disclaimer: rx.Var
) -> rx.Component:
    """
    Burbuja de chat reutilizable que recibe Vars tipadas directamente.
    """
    return rx.box(
        # Encabezado (Sovereign AI + badge de tendencia)
        rx.hstack(
            rx.icon(tag="bot", size=18, color="#D4AF37"),
            rx.text(
                "Sovereign AI", font_size="0.85rem", font_weight="bold", color="#D4AF37"
            ),
            rx.spacer(),
            rx.badge(
                tendencia,
                variant="soft",
                color_scheme=rx.cond(
                    tendencia == "ALCISTA",
                    "green",
                    rx.cond(tendencia == "BAJISTA", "red", "gray"),
                ),
            ),
            width="100%",
            margin_bottom="0.75rem",
        ),
        # Lista de sugerencias pedagógicas
        rx.vstack(
            rx.foreach(sugerencias, _sugerencia_item),
            margin_bottom="1rem",
            spacing="3",
            width="100%",
            align_items="start",
        ),
        # Disclaimer obligatorio
        rx.box(
            rx.hstack(
                rx.icon(tag="triangle-alert", size=14, color="#fbbf24"),
                rx.text(
                    disclaimer,
                    font_size="0.75rem",
                    color="#fbbf24",
                    font_weight="500",
                ),
                align_items="center",
                spacing="2",
            ),
            background_color="rgba(251, 191, 36, 0.1)",
            padding="0.5rem",
            border_radius="0.375rem",
            border_left="3px solid #fbbf24",
        ),
        # Estilo glassmorphism / burbuja de chat
        background_color="rgba(30, 35, 45, 0.85)",
        backdrop_filter="blur(10px)",
        border="1px solid rgba(255, 255, 255, 0.07)",
        border_radius="1rem 1rem 1rem 0",
        padding="1.25rem",
        box_shadow="0 4px 20px rgba(0, 0, 0, 0.25)",
        width="100%",
        margin_top="0.75rem",
    )


def ai_recommendation_widget(ticker: str) -> rx.Component:
    """
    Widget completo: botón de sugerencias + burbuja de chat con vars tipadas por ticker.
    """
    # Seleccionamos las vars correctas según el ticker en tiempo de compilación
    if ticker.upper() == "XAU":
        loaded = RecommendationsState.xau_loaded
        loading = RecommendationsState.xau_loading
        tendencia = RecommendationsState.xau_tendencia
        sugerencias = RecommendationsState.xau_sugerencias
        disclaimer = RecommendationsState.xau_disclaimer
    else:
        loaded = RecommendationsState.wti_loaded
        loading = RecommendationsState.wti_loading
        tendencia = RecommendationsState.wti_tendencia
        sugerencias = RecommendationsState.wti_sugerencias
        disclaimer = RecommendationsState.wti_disclaimer

    return rx.vstack(
        # Botón de acción
        rx.button(
            rx.icon(tag="sparkles", size=16),
            f"Sugerencias IA ({ticker.upper()})",
            on_click=RecommendationsState.generar_sugerencia(ticker),
            is_loading=loading,
            size="2",
            variant="surface",
            color_scheme="amber",
            border_radius="2rem",
        ),
        # Burbuja de chat (solo visible cuando hay datos)
        rx.cond(loaded, _chat_bubble(tendencia, sugerencias, disclaimer), rx.box()),
        # Mensaje de error
        rx.cond(
            RecommendationsState.error_msg != "",
            rx.text(
                RecommendationsState.error_msg,
                color="red",
                font_size="0.8rem",
                margin_top="0.5rem",
            ),
            rx.box(),
        ),
        align_items="start",
        margin_top="1rem",
        width="100%",
        spacing="2",
    )
