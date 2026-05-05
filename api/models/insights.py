"""
Sovereign Insights — Pydantic Models
Archivo: api/models/insights.py

Define los contratos de datos para el motor de IA del CRM.
"""
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date


class AlertaMercado(BaseModel):
    """
    Modelo de datos para una Alerta Rápida generada por el LLM.
    Representa una anomalía detectada en el precio de un activo.
    """
    tipo_alerta: str = Field(
        ...,
        description="Activo afectado, e.g. 'XAU', 'WTI'",
        examples=["XAU", "WTI"]
    )
    titulo: str = Field(
        ...,
        description="Titular breve de la alerta (máx. 80 caracteres)",
        max_length=80
    )
    mensaje: str = Field(
        ...,
        description="Explicación pedagógica de la anomalía para el inversor novato"
    )
    nivel_severidad: Literal["INFORMATIVO", "MODERADO", "CRITICO"] = Field(
        ...,
        description="Nivel de urgencia de la alerta"
    )

    class Config:
        # Ejemplo para la documentación Swagger de FastAPI
        json_schema_extra = {
            "example": {
                "tipo_alerta": "WTI",
                "titulo": "El petróleo cae un 3.2% en menos de 30 minutos",
                "mensaje": (
                    "El crudo WTI ha experimentado una caída brusca posiblemente "
                    "relacionada con datos de inventarios de la EIA. Para un inversor "
                    "novato, esto significa que el mercado está reaccionando a más "
                    "oferta de la esperada. Es un momento para observar, no para entrar."
                ),
                "nivel_severidad": "MODERADO"
            }
        }


class LeccionDelDia(BaseModel):
    """Sub-modelo para la lección pedagógica embebida en el Resumen Diario."""
    concepto: str = Field(
        ...,
        description="Nombre del concepto financiero enseñado",
        examples=["Correlación inversa dólar-oro"]
    )
    explicacion: str = Field(
        ...,
        description="Explicación simple del concepto, sin jerga técnica"
    )


class ResumenDiario(BaseModel):
    """
    Modelo de datos para el Resumen Diario generado por el LLM al cierre del mercado.
    Integra datos reales de yfinance con análisis pedagógico de la IA.
    """
    fecha_resumen: str = Field(
        ...,
        description="Fecha de la jornada en formato ISO 8601 (YYYY-MM-DD)",
        examples=[str(date.today())]
    )
    titulo_jornada: str = Field(
        ...,
        description="Titular atractivo que resume el día en los mercados"
    )
    resumen_oro: str = Field(
        ...,
        description="Análisis breve del comportamiento del Oro (XAU/USD) en la jornada"
    )
    resumen_petroleo: str = Field(
        ...,
        description="Análisis breve del comportamiento del Petróleo (WTI) en la jornada"
    )
    leccion_del_dia: LeccionDelDia = Field(
        ...,
        description="Concepto financiero del día, explicado de forma pedagógica"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "fecha_resumen": str(date.today()),
                "titulo_jornada": "El oro brilla en un día de incertidumbre global",
                "resumen_oro": (
                    "El XAU/USD cerró al alza un 1.4%, impulsado por la cautela de los "
                    "inversores ante datos de inflación en EE.UU. superiores a lo esperado. "
                    "El oro cumplió su rol histórico de 'refugio seguro'."
                ),
                "resumen_petroleo": (
                    "El WTI cerró prácticamente plano (-0.2%), con los inventarios de la "
                    "EIA mostrando un leve descenso. El mercado está en un estado de "
                    "equilibrio entre la demanda asiática y la producción de la OPEP+."
                ),
                "leccion_del_dia": {
                    "concepto": "Refugio seguro (Safe Haven)",
                    "explicacion": (
                        "En finanzas, un 'refugio seguro' es un activo que tiende a "
                        "mantener o aumentar su valor cuando los mercados caen o hay "
                        "pánico. El oro es el ejemplo clásico: cuando hay miedo, los "
                        "inversores venden acciones y compran oro."
                    )
                }
            }
        }
