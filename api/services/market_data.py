import yfinance as yf
import pandas as pd
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
        
        # Determine interval based on period
        interval = "1d"
        if period == "1d":
            interval = "5m"
        elif period == "5d":
            interval = "15m"
        elif period in ["1mo", "3mo"]:
            interval = "1d"
        elif period in ["6mo", "1y", "ytd"]:
            interval = "1wk"
        else:
            interval = "1mo"
            
        data = ticker.history(period=period, interval=interval)
        
        # Calculate Technical Indicators
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        
        # Bollinger Bands (SMA_20 ± 2 * STD_20)
        data['STD_20'] = data['Close'].rolling(window=20).std()
        data['BB_UPPER'] = data['SMA_20'] + (data['STD_20'] * 2)
        data['BB_LOWER'] = data['SMA_20'] - (data['STD_20'] * 2)
        
        history = []
        for index, row in data.iterrows():
            # Format datetime based on intraday or daily
            if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
                date_str = index.strftime('%Y-%m-%d %H:%M')
            else:
                date_str = index.strftime('%Y-%m-%d')
                
            history.append({
                "date": date_str,
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume']),
                "sma20": round(float(row['SMA_20']), 2) if not pd.isna(row['SMA_20']) else None,
                "sma50": round(float(row['SMA_50']), 2) if not pd.isna(row['SMA_50']) else None,
                "bb_upper": round(float(row['BB_UPPER']), 2) if not pd.isna(row['BB_UPPER']) else None,
                "bb_lower": round(float(row['BB_LOWER']), 2) if not pd.isna(row['BB_LOWER']) else None
            })
        return history
    except Exception as e:
        print(f"[Market Service] Error fetching historical {symbol}: {e}")
        return []

import os
import requests
import random

def get_market_news(symbols: list[str] = None, max_items: int = 8) -> list[dict]:
    """
    Returns realistic financial news for the frontend dashboard.
    Intenta obtener noticias reales de NewsAPI. Si falla, usa datos simulados como respaldo.
    """
    news_items = []
    
    # 1. Intentar obtener noticias reales de NewsAPI
    from dotenv import load_dotenv
    load_dotenv(override=True)
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if newsapi_key:
        try:
            # Buscamos términos financieros generales en español
            query = '("bolsa de valores" OR "mercado financiero" OR "Wall Street" OR "acciones" OR "S&P 500" OR "Ibex 35" OR "inversión")'
            url = f'https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&pageSize={max_items}&apiKey={newsapi_key}'
            
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                articles = data.get("articles", [])
                
                if articles:
                    for art in articles:
                        title = art.get("title", "Noticia Financiera")
                        url_noticia = art.get("url", "#")
                        publisher = art.get("source", {}).get("name", "Portal Financiero")
                            
                        news_items.append({
                            "title": title,
                            "url": url_noticia,
                            "publisher": publisher,
                            "publish_time": random.randint(5, 59),
                            "asset": "Mercados",
                            "asset_color": "#99907c"
                        })
                    return news_items
        except Exception as e:
            print(f"[Market Service] Error fetching real news from NewsAPI: {e}")
            
    # 2. Fallback: Datos simulados si NewsAPI falla o no hay API Key
    mock_news = [
        {"title": "Dónde encontrar oportunidades en Bolsa española, con CaixaBank AM", "url": "https://www.expansion.com/podcasts/en-accion/2026/05/06/69fb5543468aeb267f8b45ce.html", "publisher": "Expansión"},
        {"title": "La Primera de Expansión sobre Bolsa, López Miras, Santander y GameStop", "url": "https://www.expansion.com/podcasts/la-primera-de-expansion/2026/05/04/69f82a20468aeb41058b45ad.html", "publisher": "Expansión"},
        {"title": "Si te ofrecen 10.000 euros a cambio de no comprar un iPhone nunca más, ¿aceptarías?", "url": "https://www.applesfera.com/curiosidades/te-ofrecen-10-000-euros-a-cambio-no-comprar-iphone-nunca-aceptarias-warren-buffett-apuesta-a-que-no", "publisher": "Applesfera"},
        {"title": "Steve Wozniak podría ser uno de los hombres más ricos del planeta tras cofundar Apple", "url": "https://www.applesfera.com/curiosidades/steve-wozniak-podria-ser-uno-hombres-ricos-planeta-cofundar-apple-siempre-ha-preferido-regalar-parte-su-fortuna", "publisher": "Applesfera"},
        {"title": "La verdadera razón por la que Tim Cook lee cada mañana los emails que recibe de los usuarios", "url": "https://www.applesfera.com/curiosidades/verdadera-razon-que-tim-cook-lee-cada-manana-emails-que-recibe-usuarios", "publisher": "Applesfera"},
        {"title": "\"No lo construimos en un garaje, es inventado\". Wozniak cuenta la verdadera historia", "url": "https://www.applesfera.com/curiosidades/no-construimos-garaje-inventado-steve-wozniak-cuenta-verdadera-historia-detras-creacion-apple-a-steve-jobs", "publisher": "Applesfera"}
    ]
    
    for item in mock_news:
        news_items.append({
            "title": item["title"],
            "url": item["url"],
            "publisher": item["publisher"],
            "publish_time": random.randint(10, 120),
            "asset": "Mercados",
            "asset_color": "#99907c"
        })
        
    random.shuffle(news_items)
    return news_items[:max_items]
