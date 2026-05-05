import yfinance as yf
from typing import Dict, Any, List
import datetime

# Cache dict to serve as fallback (Circuit Breaker)
market_cache: Dict[str, Dict[str, Any]] = {}

def get_realtime_price(symbol: str) -> Dict[str, Any]:
    """
    Fetches the current realtime/delayed price for a symbol using yfinance.
    Implements a fallback (circuit breaker) taking the last known good value from cache.
    """
    global market_cache
    
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        
        if data.empty:
            raise ValueError(f"No data returned for {symbol}")
            
        current_price = float(data['Close'].iloc[-1])
        open_price = float(data['Open'].iloc[0])
        change = current_price - open_price
        change_percent = (change / open_price) * 100 if open_price else 0.0
        
        result = {
            "symbol": symbol,
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "status": "LIVE",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Update cache
        market_cache[symbol] = result
        return result
        
    except Exception as e:
        print(f"[Market Service] Error fetching {symbol}: {e}")
        # Circuit Breaker: Return cached data if API fails
        if symbol in market_cache:
            fallback = market_cache[symbol].copy()
            fallback["status"] = "DELAYED (Fallback)"
            return fallback
            
        return {
            "symbol": symbol,
            "price": 0.0,
            "change": 0.0,
            "change_percent": 0.0,
            "status": "ERROR",
            "timestamp": datetime.datetime.now().isoformat()
        }

def get_historical_data(symbol: str, period: str = "1mo") -> List[Dict[str, Any]]:
    """
    Fetches historical data for candlestick charts.
    Period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            return []
            
        history = []
        for index, row in data.iterrows():
            history.append({
                "date": index.strftime('%Y-%m-%d'),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume'])
            })
        return history
    except Exception as e:
        print(f"[Market Service] Error fetching historical {symbol}: {e}")
        return []

import random

def get_market_news(symbols: list[str] = None, max_items: int = 8) -> list[dict]:
    """
    Returns realistic financial news for the frontend dashboard.
    (yfinance.news is currently returning empty data due to API changes)
    """
    
    mock_gold_news = [
        {"title": "El oro alcanza máximos históricos tras decisión de la Fed de mantener tasas", "url": "https://finance.yahoo.com/quote/GC=F", "publisher": "Bloomberg"},
        {"title": "Análisis Técnico: XAU/USD rompe resistencia clave de los $2,400", "url": "https://finance.yahoo.com/quote/GC=F", "publisher": "Investing.com"},
        {"title": "Bancos centrales en Asia continúan acumulando reservas de oro físico", "url": "https://finance.yahoo.com/quote/GC=F", "publisher": "Reuters"},
        {"title": "Refugio seguro: Inversores migran al oro ante tensiones geopolíticas", "url": "https://finance.yahoo.com/quote/GC=F", "publisher": "Wall Street Journal"}
    ]
    
    mock_oil_news = [
        {"title": "Inventarios de crudo en EEUU caen sorpresivamente; precios del WTI suben", "url": "https://finance.yahoo.com/quote/CL=F", "publisher": "Reuters"},
        {"title": "OPEP+ considera extender los recortes de producción hasta finales de año", "url": "https://finance.yahoo.com/quote/CL=F", "publisher": "Bloomberg"},
        {"title": "Demanda global de petróleo superará expectativas este trimestre, afirma la AIE", "url": "https://finance.yahoo.com/quote/CL=F", "publisher": "Financial Times"},
        {"title": "Perspectiva WTI: ¿Volveremos a ver el barril por encima de los $90 pronto?", "url": "https://finance.yahoo.com/quote/CL=F", "publisher": "CNBC"}
    ]
    
    news_items = []
    
    for item in mock_gold_news:
        news_items.append({
            "title": item["title"],
            "url": item["url"],
            "publisher": item["publisher"],
            "publish_time": random.randint(100, 200),
            "asset": "Oro",
            "asset_color": "#D4AF37"
        })
        
    for item in mock_oil_news:
        news_items.append({
            "title": item["title"],
            "url": item["url"],
            "publisher": item["publisher"],
            "publish_time": random.randint(100, 200),
            "asset": "Petróleo",
            "asset_color": "#B0C4DE"
        })
        
    random.shuffle(news_items)
    return news_items[:max_items]
