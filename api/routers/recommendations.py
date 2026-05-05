from fastapi import APIRouter, HTTPException
from api.models.recommendations import RecomendacionIA
from api.services.recommendations_service import generar_recomendacion

router = APIRouter(
    prefix="/recommendations",
    tags=["AI Recommendations"]
)

@router.get("/{ticker}", response_model=RecomendacionIA)
async def get_ai_recommendation(ticker: str):
    """
    Genera una recomendación financiera pedagógica utilizando inteligencia artificial
    para el activo especificado (ej. XAU, WTI).
    """
    try:
        recomendacion = await generar_recomendacion(ticker)
        return recomendacion
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al generar sugerencia IA: {str(e)}")
