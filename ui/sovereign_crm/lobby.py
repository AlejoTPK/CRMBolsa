import reflex as rx
from .components import COLORS, glass_card

def lobby_navbar() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.heading("Sovereign", size="6", color=COLORS["primary"], font_family="serif"),
            rx.spacer(),
            rx.hstack(
                rx.link("Intelligence", href="#intelligence", color=COLORS["text_main"], _hover={"color": COLORS["primary"]}),
                rx.link("Portafolio", href="#portafolio", color=COLORS["text_main"], _hover={"color": COLORS["primary"]}),
                rx.link("Vault", href="#vault", color=COLORS["text_main"], _hover={"color": COLORS["primary"]}),
                rx.link("Planes", href="#pricing", color=COLORS["text_main"], _hover={"color": COLORS["primary"]}),
                spacing="5",
            ),
            rx.spacer(),
            rx.button(
                "Acceder al Dashboard",
                bg="transparent",
                color=COLORS["primary"],
                border=f"1px solid {COLORS['primary']}",
                _hover={"bg": COLORS["primary_subtle"]},
                on_click=rx.redirect("/dashboard"),
                cursor="pointer",
            ),
            width="100%",
            max_width="1400px",
            margin="0 auto",
            align_items="center",
        ),
        width="100%",
        padding="1rem 2rem",
        border_bottom=f"1px solid {COLORS['text_muted']}25",
        bg=f"{COLORS['surface']}EE", 
        backdrop_filter="blur(10px)",
        position="sticky",
        top="0",
        z_index="999",
    )

def feature_card(icon: str, title: str, description: str, delay: str) -> rx.Component:
    return glass_card(
        rx.vstack(
            rx.icon(icon, color=COLORS["primary"], size=24),
            rx.heading(title, size="4", color=COLORS["text_main"], font_family="serif"),
            rx.text(description, color=COLORS["text_muted"], size="2", line_height="1.6"),
            spacing="3",
            align_items="start",
        ),
        style={
            "animation": f"fadeIn 0.8s ease-out {delay} backwards",
            "cursor": "default",
            "transition": "transform 0.3s ease, box-shadow 0.3s ease",
            "_hover": {
                "transform": "translateY(-5px)",
                "box_shadow": f"0 10px 20px {COLORS['primary_glow']}"
            }
        }
    )

def lobby_hero() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.badge("PREMIUM FINANCIAL ENGINE", color_scheme="yellow", variant="surface", size="2", style={"animation": "fadeIn 0.6s ease-out"}),
            rx.heading(
                "Sovereign Intelligence.",
                size="9",
                color=COLORS["text_main"],
                font_family="serif",
                line_height="1.1",
                style={"animation": "fadeIn 0.8s ease-out 0.2s backwards"}
            ),
            rx.text(
                "Precision-engineered real-time market data for the modern investor.",
                size="4",
                color=COLORS["text_muted"],
                max_width="500px",
                style={"animation": "fadeIn 0.8s ease-out 0.4s backwards"}
            ),
            rx.hstack(
                rx.button(
                    "Entrar al App",
                    bg=COLORS["primary"],
                    color="#000",
                    size="3",
                    on_click=rx.redirect("/dashboard"),
                    _hover={"box_shadow": f"0 0 20px {COLORS['primary_glow']}", "opacity": 0.9},
                    transition="all 0.3s ease",
                    style={"animation": "fadeIn 0.8s ease-out 0.6s backwards"},
                    cursor="pointer",
                ),
                rx.link(
                    rx.button(
                        "Conoce Más",
                        variant="surface",
                        bg="transparent",
                        color=COLORS["text_main"],
                        border=f"1px solid {COLORS['text_muted']}40",
                        size="3",
                        _hover={"bg": COLORS["surface_high"], "border_color": COLORS["text_muted"]},
                        style={"animation": "fadeIn 0.8s ease-out 0.6s backwards"},
                        cursor="pointer",
                    ),
                    href="#intelligence"
                ),
                spacing="4",
                margin_top="1rem"
            ),
            spacing="4",
            align_items="start",
            width="50%",
        ),
        rx.spacer(),
        rx.box(
            glass_card(
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.box(width="8px", height="8px", bg="red", border_radius="full", style={"animation": "pulse 2s infinite"}),
                            rx.text("LIVE", color="red", font_weight="bold", size="1"),
                            align_items="center",
                            spacing="1"
                        ),
                        rx.spacer(),
                        rx.text("XAU/USD", color=COLORS["text_main"], font_weight="bold"),
                        width="100%"
                    ),
                    rx.heading("$2,345.60", color=COLORS["primary"], size="7", font_family="serif"),
                    rx.text("+12.40 (0.53%)", color=COLORS["success"], size="2"),
                    rx.box(
                        width="100%", height="60px", bg=f"linear-gradient(180deg, {COLORS['primary_subtle']} 0%, transparent 100%)",
                        border_top=f"2px solid {COLORS['primary']}", border_radius="4px", margin_top="1rem"
                    ),
                    align_items="start",
                    width="100%"
                ),
                style={
                    "width": "350px",
                    "animation": "float 6s ease-in-out infinite",
                    "box_shadow": f"0 24px 48px {COLORS['primary_glow']}"
                }
            ),
            width="50%",
            display="flex",
            justify_content="flex-end"
        ),
        width="100%",
        align_items="center",
        padding_top="8rem",
        padding_bottom="4rem",
    )

def lobby_social_proof() -> rx.Component:
    return rx.vstack(
        rx.text("FUENTES DE DATOS INSTITUCIONALES Y TECNOLOGÍA DE CONFIANZA", color=COLORS["text_muted"], size="1", font_weight="bold", letter_spacing="2px"),
        rx.hstack(
            rx.heading("NASDAQ", size="5", color=COLORS["text_muted"], font_family="serif", opacity="0.6"),
            rx.heading("Bloomberg", size="5", color=COLORS["text_muted"], font_family="serif", opacity="0.6"),
            rx.heading("Reuters", size="5", color=COLORS["text_muted"], font_family="serif", opacity="0.6"),
            rx.heading("NYSE", size="5", color=COLORS["text_muted"], font_family="serif", opacity="0.6"),
            rx.heading("Groq AI", size="5", color=COLORS["text_muted"], font_family="serif", opacity="0.6"),
            spacing="8",
            wrap="wrap",
            justify_content="center",
        ),
        spacing="6",
        align_items="center",
        padding_y="4rem",
        width="100%",
        border_bottom=f"1px solid {COLORS['text_muted']}15"
    )

def feature_section(id: str, title: str, description: str, is_reversed: bool = False, mockup_content: rx.Component = None) -> rx.Component:
    text_content = rx.vstack(
        rx.heading(title, size="8", color=COLORS["text_main"], font_family="serif"),
        rx.text(description, color=COLORS["text_muted"], size="4", line_height="1.8"),
        rx.button("Aprender más", variant="ghost", color=COLORS["primary"], margin_top="1rem", cursor="pointer"),
        spacing="4",
        align_items="start",
        width="100%"
    )
    
    if not is_reversed:
        layout = rx.hstack(rx.box(text_content, width="50%"), rx.spacer(), rx.box(mockup_content, width="45%"), width="100%", align_items="center")
    else:
        layout = rx.hstack(rx.box(mockup_content, width="45%"), rx.spacer(), rx.box(text_content, width="50%"), width="100%", align_items="center")
    
    return rx.box(layout, id=id, padding_y="6rem", width="100%")

def lobby_feature_sections() -> rx.Component:
    intelligence_mockup = glass_card(
        rx.vstack(
            rx.hstack(rx.icon("activity", color=COLORS["primary"]), rx.text("Proyección Groq AI", color=COLORS["primary"], size="2", font_weight="bold"), align_items="center"),
            rx.box(width="100%", height="150px", bg=f"linear-gradient(90deg, {COLORS['primary_subtle']} 0%, transparent 100%)", border_bottom=f"2px solid {COLORS['primary']}"),
            rx.hstack(rx.badge("BUY SIGNAL", color_scheme="green"), rx.text("Precisión 94%", color=COLORS["text_muted"], size="2")),
            spacing="3",
            width="100%",
            align_items="start"
        ), style={"box_shadow": f"0 10px 30px {COLORS['primary_glow']}", "transform": "perspective(1000px) rotateY(-5deg)"}
    )

    portafolio_mockup = glass_card(
        rx.vstack(
            rx.text("Distribución de Activos", color=COLORS["text_main"], font_weight="bold"),
            rx.hstack(
                rx.box(width="40px", height="100px", bg=COLORS["primary"], border_radius="4px"),
                rx.box(width="40px", height="60px", bg=COLORS["text_muted"], border_radius="4px"),
                rx.box(width="40px", height="80px", bg="#4CAF50", border_radius="4px"),
                rx.box(width="40px", height="120px", bg=COLORS["primary_subtle"], border_radius="4px"),
                spacing="4",
                align_items="end",
                height="140px"
            ),
            spacing="4",
            width="100%",
            align_items="center"
        ), style={"box_shadow": f"0 10px 30px rgba(0,0,0,0.5)", "transform": "perspective(1000px) rotateY(5deg)"}
    )

    vault_mockup = glass_card(
        rx.vstack(
            rx.icon("shield-check", color=COLORS["primary"], size=64),
            rx.text("Encriptación AES-256", color=COLORS["text_main"], font_weight="bold", size="4"),
            rx.text("Historial de transacciones asegurado a nivel militar.", color=COLORS["text_muted"], size="2", text_align="center"),
            spacing="4",
            width="100%",
            align_items="center"
        ), style={"box_shadow": f"0 10px 30px {COLORS['primary_glow']}", "transform": "perspective(1000px) rotateY(-5deg)"}
    )

    return rx.vstack(
        feature_section("intelligence", "Inteligencia Predictiva", "Modelos fundacionales entrenados con miles de millones de puntos de datos procesan el mercado en milisegundos, entregando predicciones que los humanos no pueden ver.", False, intelligence_mockup),
        feature_section("portafolio", "Diversificación Estratégica", "Visualiza, rebalancea y optimiza tu portafolio con herramientas que reducen el riesgo y maximizan el retorno absoluto en tiempo real.", True, portafolio_mockup),
        feature_section("vault", "Seguridad Inquebrantable", "Infraestructura construida con los mismos estándares que los bancos centrales. Tu historial y tus estrategias están encriptadas de extremo a extremo.", False, vault_mockup),
        width="100%",
        spacing="0",
        padding_y="4rem"
    )

def market_badge(symbol: str, name: str, price: str, change: str, is_up: bool) -> rx.Component:
    color = COLORS["success"] if is_up else "red"
    return glass_card(
        rx.vstack(
            rx.hstack(rx.text(symbol, font_weight="bold", color=COLORS["text_main"]), rx.spacer(), rx.text(name, size="1", color=COLORS["text_muted"]), width="100%"),
            rx.heading(price, size="5", color=color, font_family="serif"),
            rx.text(change, size="2", color=color),
            spacing="2",
            width="100%"
        ),
        style={
            "transition": "transform 0.3s ease",
            "_hover": {"transform": "translateY(-5px)", "box_shadow": f"0 8px 24px rgba(0,0,0,0.4)"}
        }
    )

def lobby_markets_grid() -> rx.Component:
    return rx.vstack(
        rx.heading("Mercados Globales Soportados", size="8", color=COLORS["text_main"], font_family="serif", margin_bottom="2rem"),
        rx.grid(
            market_badge("XAU/USD", "Oro Físico", "$2,345.60", "+0.53%", True),
            market_badge("WTI", "Crudo Texas", "$78.40", "-1.20%", False),
            market_badge("SPX", "S&P 500", "$5,230.10", "+0.80%", True),
            market_badge("EUR/USD", "Euro", "$1.0845", "+0.15%", True),
            market_badge("BTC/USD", "Bitcoin", "$64,300", "-2.50%", False),
            market_badge("NDX", "Nasdaq 100", "$18,200", "+1.10%", True),
            columns="3",
            spacing="4",
            width="100%"
        ),
        padding_y="6rem",
        width="100%",
        border_bottom=f"1px solid {COLORS['text_muted']}15"
    )

def pricing_card(title: str, price: str, features: list, is_highlighted: bool = False) -> rx.Component:
    bg = COLORS["surface"] if not is_highlighted else f"{COLORS['primary_subtle']}15"
    border = f"1px solid {COLORS['text_muted']}30" if not is_highlighted else f"1px solid {COLORS['primary']}"
    shadow = "none" if not is_highlighted else f"0 10px 40px {COLORS['primary_glow']}"
    
    return rx.box(
        rx.vstack(
            rx.badge("Más Popular", color_scheme="yellow") if is_highlighted else rx.box(height="22px"),
            rx.heading(title, size="6", color=COLORS["text_main"]),
            rx.hstack(rx.heading(price, size="8", color=COLORS["primary"], font_family="serif"), rx.text("/mes", color=COLORS["text_muted"], size="2"), align_items="baseline"),
            rx.divider(border_color=f"{COLORS['text_muted']}30", margin_y="1rem"),
            rx.vstack(
                *[rx.hstack(rx.icon("check", color=COLORS["primary"], size=16), rx.text(f, color=COLORS["text_muted"], size="2")) for f in features],
                align_items="start",
                spacing="3",
                min_height="180px"
            ),
            rx.button("Seleccionar Plan", width="100%", cursor="pointer", bg=COLORS["primary"] if is_highlighted else "transparent", color="#000" if is_highlighted else COLORS["primary"], border=f"1px solid {COLORS['primary']}", margin_top="2rem"),
            spacing="4",
            align_items="start",
            width="100%",
        ),
        bg=bg,
        border=border,
        border_radius="12px",
        padding="2rem",
        box_shadow=shadow,
        transition="transform 0.3s ease",
        _hover={"transform": "translateY(-10px)"}
    )

def lobby_pricing() -> rx.Component:
    return rx.vstack(
        rx.heading("Niveles de Acceso", size="8", color=COLORS["text_main"], font_family="serif", margin_bottom="1rem"),
        rx.text("Invierte con la mejor inteligencia del mercado a tu medida.", color=COLORS["text_muted"], size="4", margin_bottom="3rem"),
        rx.grid(
            pricing_card("Starter", "$29", ["Datos con 15min de retraso", "Análisis básico de mercado", "3 Alertas IA por día"]),
            pricing_card("Pro", "$99", ["Streaming en Tiempo Real", "Alertas IA Predictivas Ilimitadas", "Gestión Avanzada de Portafolio", "Acceso a Commodities y Forex"], True),
            pricing_card("Institutional", "$499", ["Acceso API WebSockets", "Exportación de bases de datos", "Soporte dedicado 24/7", "Infraestructura privada encriptada"]),
            columns="3",
            spacing="6",
            width="100%"
        ),
        id="pricing",
        padding_y="6rem",
        width="100%",
        align_items="center"
    )

def faq_item(question: str, answer: str) -> rx.Component:
    return rx.vstack(
        rx.heading(question, size="4", color=COLORS["text_main"]),
        rx.text(answer, color=COLORS["text_muted"], size="3", line_height="1.6"),
        width="100%",
        padding_y="1rem",
        border_bottom=f"1px solid {COLORS['text_muted']}20",
        spacing="2",
        align_items="start"
    )

def lobby_faq() -> rx.Component:
    return rx.vstack(
        rx.heading("Preguntas Frecuentes", size="8", color=COLORS["text_main"], font_family="serif", margin_bottom="2rem"),
        rx.vstack(
            faq_item("¿Cuál es la latencia de los datos en tiempo real?", "Nuestra infraestructura de WebSockets procesa los ticks del mercado en menos de 50ms para usuarios Pro e Institucionales."),
            faq_item("¿Qué métodos de pago aceptan?", "Aceptamos todas las tarjetas de crédito principales y pagos corporativos mediante transferencia bancaria Swift/SEPA."),
            faq_item("¿Mi información de portafolio está segura?", "Completamente. Utilizamos encriptación AES-256 de extremo a extremo. Sovereign CRM nunca tiene acceso directo a tus claves privadas o fondos de tu broker."),
            width="100%",
            spacing="4"
        ),
        padding_y="6rem",
        width="100%",
        max_width="800px",
        margin="0 auto"
    )

def lobby_final_cta() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("Comienza a optimizar tu portafolio hoy.", size="8", color=COLORS["text_main"], font_family="serif", text_align="center"),
            rx.text("Únete a la nueva era de la inteligencia financiera sin compromisos.", color=COLORS["text_muted"], size="4", margin_bottom="2rem"),
            rx.button(
                "Crear Cuenta Premium",
                size="4",
                bg=COLORS["primary"],
                color="#000",
                _hover={"box_shadow": f"0 0 20px {COLORS['primary_glow']}", "transform": "scale(1.05)"},
                transition="all 0.3s ease",
                cursor="pointer",
                on_click=rx.redirect("/dashboard")
            ),
            align_items="center",
            spacing="4"
        ),
        width="100%",
        padding="6rem 2rem",
        border_radius="16px",
        background=f"linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['background']} 100%)",
        border=f"1px solid {COLORS['primary']}30",
        box_shadow=f"0 20px 60px rgba(0,0,0,0.5)",
        margin_bottom="6rem"
    )

def lobby_footer() -> rx.Component:
    return rx.vstack(
        rx.divider(border_color=f"{COLORS['text_muted']}25"),
        rx.hstack(
            rx.text("© 2026 Sovereign CRM. All rights reserved.", color=COLORS["text_muted"], size="2"),
            rx.spacer(),
            rx.text("Senior Engineer Grade.", color=COLORS["text_muted"], size="1", font_family="monospace", opacity="0.5"),
            width="100%",
            padding_y="2rem"
        ),
        width="100%"
    )

# Inline CSS for Animations and Global Styles
css_animations = """
<style>
html { scroll-behavior: smooth; }
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-15px); }
    100% { transform: translateY(0px); }
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0px); }
}
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.3; }
    100% { opacity: 1; }
}
@keyframes twinkle {
    0% { opacity: 0; transform: scale(0.5); }
    50% { opacity: 0.4; transform: scale(1.5); }
    100% { opacity: 0; transform: scale(0.5); }
}
</style>
"""

def background_sparkles() -> rx.Component:
    sparkles = []
    # Posiciones y tiempos predefinidos para los destellos (left%, top%, duration, delay)
    positions = [
        (15, 25, "3s", "0s"), (85, 15, "4s", "1s"), (45, 55, "5s", "2s"), (75, 65, "3.5s", "0.5s"), (25, 85, "4.5s", "1.5s"),
        (95, 80, "5.5s", "2.5s"), (5, 70, "3.2s", "0.2s"), (55, 10, "4.8s", "1.8s"), (65, 90, "3.7s", "0.7s"), (35, 35, "5.2s", "2.2s"),
        (20, 10, "4s", "0s"), (80, 50, "5s", "1s"), (10, 90, "6s", "2s"), (50, 75, "4.5s", "1.5s"), (90, 30, "3.5s", "0.5s")
    ]
    for left, top, duration, delay in positions:
        sparkles.append(
            rx.box(
                width="2px",
                height="2px",
                border_radius="50%",
                bg=COLORS["primary"],
                box_shadow=f"0 0 10px 2px {COLORS['primary']}",
                position="absolute",
                left=f"{left}%",
                top=f"{top}%",
                opacity="0",
                style={"animation": f"twinkle {duration} infinite ease-in-out {delay}"}
            )
        )
    return rx.box(
        *sparkles,
        position="fixed",
        width="100vw",
        height="100vh",
        top="0",
        left="0",
        z_index="0",
        pointer_events="none"
    )

def lobby_view() -> rx.Component:
    """The main Landing Page (Lobby)."""
    return rx.box(
        rx.html(css_animations),
        background_sparkles(),
        lobby_navbar(),
        rx.vstack(
            lobby_hero(),
            lobby_social_proof(),
            
            # The 3 feature cards below social proof
            rx.box(
                rx.grid(
                    feature_card("activity", "Análisis en Tiempo Real", "Streaming de datos sub-segundo con latencia optimizada para ejecución rápida.", "0.8s"),
                    feature_card("shield", "Portafolio Optimizado", "Gestión de riesgo impulsada por IA, rebalanceo inteligente y exposición controlada.", "1.0s"),
                    feature_card("cpu", "Alertas IA", "Análisis de sentimiento de mercado predictivo usando modelos fundacionales avanzados.", "1.2s"),
                    columns="3",
                    spacing="6",
                    width="100%",
                ),
                padding_y="6rem",
                width="100%"
            ),

            lobby_feature_sections(),
            lobby_markets_grid(),
            lobby_pricing(),
            lobby_faq(),
            lobby_final_cta(),
            lobby_footer(),
            width="100%",
            max_width="1400px",
            margin="0 auto",
            padding_x="2rem"
        ),
        bg=COLORS["background"],
        min_height="100vh",
        width="100%"
    )
