from pydantic import BaseModel, Field
from typing import Literal, List

class RecomendacionIA(BaseModel):
    """
    Modelo estricto para validar la respuesta del LLM (Groq) respecto a recomendaciones.
    """
    ticker: str = Field(
        ...,
        description="Símbolo del activo analizado, e.g. 'XAU', 'WTI'",
        examples=["XAU"]
    )
    tendencia_corta: Literal["ALCISTA", "BAJISTA", "LATERAL"] = Field(
        ...,
        description="Tendencia estimada a corto plazo"
    )
    sugerencias_pedagogicas: List[str] = Field(
        ...,
        description="Lista de al menos 2 sugerencias o perspectivas de inversión explicadas de manera simple y pedagógica para un novato.",
        min_items=2
    )
    disclaimer_obligatorio: str = Field(
        ...,
        description="Aviso legal indicando explícitamente que la sugerencia es educativa y no asesoría financiera."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "WTI",
                "tendencia_corta": "LATERAL",
                "sugerencias_pedagogicas": [
                    "La volatilidad del WTI está alta debido a inventarios mixtos. Sugerimos observar cómo reacciona el precio ante la barrera de los 80 dólares antes de tomar decisiones apresuradas.",
                    "Recuerda que operar petróleo requiere atención a noticias macroeconómicas geopolíticas, no solo análisis técnico."
                ],
                "disclaimer_obligatorio": "Solo con fines educativos, no es asesoría financiera."
            }
        }
