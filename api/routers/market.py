from fastapi import APIRouter
from typing import Dict, Any, List
from api.services.market_data import get_realtime_price, get_historical_data, get_market_news

router = APIRouter(
    prefix="/market",
    tags=["Market Data"]
)

# Standard tickers for our targeted commodities
COMMODITIES = {
    "XAU": "GC=F", # Gold
    "WTI": "CL=F"  # Crude Oil
}

@router.get("/quotes")
async def get_quotes() -> Dict[str, Any]:
    """
    Returns the real-time (or delayed fallback) quotes for key commodities.
    """
    gold = get_realtime_price(COMMODITIES["XAU"])
    oil = get_realtime_price(COMMODITIES["WTI"])
    
    return {
        "gold": gold,
        "oil": oil
    }

@router.get("/history/{asset}")
async def get_history(asset: str, period: str = "1mo") -> List[Dict[str, Any]]:
    """
    Returns historical data for candlestick rendering (Reflex).
    Asset options: XAU, WTI
    """
    symbol = COMMODITIES.get(asset.upper())
    if not symbol:
        return []
        
    return get_historical_data(symbol, period)

@router.get("/news")
async def get_news(limit: int = 8) -> List[Dict[str, Any]]:
    """
    Returns real financial news for gold and oil, fetched via yfinance.
    """
    return get_market_news(max_items=limit)
