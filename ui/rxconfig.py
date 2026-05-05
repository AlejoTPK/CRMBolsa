import reflex as rx

config = rx.Config(
    app_name="sovereign_crm",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)