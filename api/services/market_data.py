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

        current_price = float(data["Close"].iloc[-1])
        open_price = float(data["Open"].iloc[0])
        change = current_price - open_price
        change_percent = (change / open_price) * 100 if open_price else 0.0

        result = {
            "symbol": symbol,
            "price": round(current_price, 2),
            "open_price": round(open_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "status": "LIVE",
            "timestamp": datetime.datetime.now().isoformat(),
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
            "timestamp": datetime.datetime.now().isoformat(),
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
        data["SMA_20"] = data["Close"].rolling(window=20).mean()
        data["SMA_50"] = data["Close"].rolling(window=50).mean()

        # Bollinger Bands (SMA_20 ± 2 * STD_20)
        data["STD_20"] = data["Close"].rolling(window=20).std()
        data["BB_UPPER"] = data["SMA_20"] + (data["STD_20"] * 2)
        data["BB_LOWER"] = data["SMA_20"] - (data["STD_20"] * 2)

        history = []
        for index, row in data.iterrows():
            # Format datetime based on intraday or daily
            if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
                date_str = index.strftime("%Y-%m-%d %H:%M")
            else:
                date_str = index.strftime("%Y-%m-%d")

            history.append(
                {
                    "date": date_str,
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]),
                    "sma20": round(float(row["SMA_20"]), 2)
                    if not pd.isna(row["SMA_20"])
                    else None,
                    "sma50": round(float(row["SMA_50"]), 2)
                    if not pd.isna(row["SMA_50"])
                    else None,
                    "bb_upper": round(float(row["BB_UPPER"]), 2)
                    if not pd.isna(row["BB_UPPER"])
                    else None,
                    "bb_lower": round(float(row["BB_LOWER"]), 2)
                    if not pd.isna(row["BB_LOWER"])
                    else None,
                }
            )
        return history
    except Exception as e:
        print(f"[Market Service] Error fetching historical {symbol}: {e}")
        return []


import os
import requests
import random
import time
import datetime

# Cache de noticias con TTL (5 minutos)
_news_cache: dict = {"data": [], "timestamp": 0.0}
_NEWS_TTL = 300

MESES_ES = {
    1: "ene",
    2: "feb",
    3: "mar",
    4: "abr",
    5: "may",
    6: "jun",
    7: "jul",
    8: "ago",
    9: "sep",
    10: "oct",
    11: "nov",
    12: "dic",
}


def _format_published_at(iso_str: str) -> str:
    """Convierte un ISO UTC a formato legible: '15 may 10:30'."""
    try:
        if iso_str.endswith("Z"):
            iso_str = iso_str[:-1] + "+00:00"
        dt = datetime.datetime.fromisoformat(iso_str)
        mes = MESES_ES.get(dt.month, dt.strftime("%b"))
        return f"{dt.day} {mes} {dt.strftime('%H:%M')}"
    except Exception:
        return ""


def get_market_news(symbols: list[str] = None, max_items: int = 8) -> list[dict]:
    """
    Returns latest relevant financial news for the frontend dashboard.
    Cachea resultados 5 min. Intenta NewsAPI primero; fallback a datos simulados.
    """
    global _news_cache

    # 1. Cache hit
    if time.time() - _news_cache["timestamp"] < _NEWS_TTL and _news_cache["data"]:
        return _news_cache["data"][:max_items]

    news_items = []

    # 2. Intentar NewsAPI con query optimizada para materias primas + mercados
    from dotenv import load_dotenv

    load_dotenv(override=True)
    newsapi_key = os.getenv("NEWSAPI_KEY")
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if newsapi_key:
        try:
            # Query bilingüe: materias primas + mercados financieros
            query = (
                '("oro" OR "petróleo" OR "crudo" OR "commodities" OR '
                '"materias primas" OR "gold" OR "oil" OR "crude" OR '
                '"bolsa" OR "mercado financiero" OR "Wall Street" OR '
                '"acciones" OR "S&P 500" OR "inversión" OR "Ibex 35")'
            )
            url = (
                f"https://newsapi.org/v2/everything"
                f"?q={query}"
                f"&language=es"
                f"&sortBy=publishedAt"
                f"&pageSize={max_items * 2}"
                f"&apiKey={newsapi_key}"
            )

            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                articles = data.get("articles", [])

                if articles:
                    for art in articles:
                        title = art.get("title", "Noticia Financiera")
                        url_noticia = art.get("url", "#")
                        publisher = art.get("source", {}).get(
                            "name", "Portal Financiero"
                        )
                        published_at = art.get("publishedAt", now_iso)
                        display_time = _format_published_at(published_at)

                        news_items.append(
                            {
                                "title": title,
                                "url": url_noticia,
                                "publisher": publisher,
                                "published_at": published_at,
                                "display_time": display_time,
                                "asset": "Mercados",
                                "asset_color": "#99907c",
                            }
                        )
                    # Cachear
                    _news_cache = {"data": news_items, "timestamp": time.time()}
                    return news_items[:max_items]
        except Exception as e:
            print(f"[Market Service] Error fetching real news from NewsAPI: {e}")

    # 3. Fallback: usar yfinance para obtener noticias reales con URLs válidas
    try:
        yf_news = _get_yfinance_news(max_items)
        if yf_news:
            _news_cache = {"data": yf_news, "timestamp": time.time()}
            return yf_news
    except Exception as e:
        print(f"[Market Service] Error fetching yfinance news: {e}")

    # 4. Último fallback: enlaces de búsqueda reales que siempre funcionan
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    search_news = [
        {
            "title": "Últimas noticias: Oro (XAU/USD) — análisis y precio en tiempo real",
            "url": "https://news.google.com/search?q=gold+price+XAU+commodities&hl=es-419",
            "publisher": "Google News",
            "published_at": now_iso,
        },
        {
            "title": "Últimas noticias: Petróleo (WTI) — cotización y análisis de crudo",
            "url": "https://news.google.com/search?q=crude+oil+WTI+price+energy&hl=es-419",
            "publisher": "Google News",
            "published_at": now_iso,
        },
        {
            "title": "Mercados financieros: Wall Street, S&P 500 y bolsas mundiales",
            "url": "https://news.google.com/search?q=stock+market+SP500+Wall+Street+today&hl=es-419",
            "publisher": "Google News",
            "published_at": now_iso,
        },
        {
            "title": "Materias primas: oro, petróleo, cobre y commodities globales",
            "url": "https://news.google.com/search?q=commodities+gold+oil+markets&hl=es-419",
            "publisher": "Google News",
            "published_at": now_iso,
        },
        {
            "title": "Bolsa española: Ibex 35, índices europeos y mercados",
            "url": "https://news.google.com/search?q=Ibex+35+bolsa+espa%C3%B1ola+mercados&hl=es",
            "publisher": "Google News",
            "published_at": now_iso,
        },
        {
            "title": "Inversiones y análisis: bancos centrales, tipos de interés y mercados",
            "url": "https://news.google.com/search?q=central+banks+interest+rates+investment&hl=es-419",
            "publisher": "Google News",
            "published_at": now_iso,
        },
        {
            "title": "Noticias económicas: PIB, inflación y datos macroeconómicos",
            "url": "https://news.google.com/search?q=economy+inflation+GDP+markets&hl=es-419",
            "publisher": "Google News",
            "published_at": now_iso,
        },
        {
            "title": "Energía y petróleo: OPEP+, Brent, WTI y geopolítica",
            "url": "https://news.google.com/search?q=OPEC+oil+energy+geopolitics&hl=es-419",
            "publisher": "Google News",
            "published_at": now_iso,
        },
    ]

    for item in search_news:
        display_time = _format_published_at(item["published_at"])
        news_items.append(
            {
                "title": item["title"],
                "url": item["url"],
                "publisher": item["publisher"],
                "published_at": item["published_at"],
                "display_time": display_time,
                "asset": "Mercados",
                "asset_color": "#99907c",
            }
        )

    random.shuffle(news_items)
    result = news_items[:max_items]

    _news_cache = {"data": result, "timestamp": time.time()}
    return result


def _get_yfinance_news(max_items: int) -> list[dict]:
    """Obtiene noticias reales via yfinance Search para commodities relevantes."""
    news_items = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    queries = ["gold commodities", "crude oil WTI", "SP500 stock market"]

    for query in queries:
        try:
            search = yf.Search(query=query, news_count=6)
            if search.news:
                for article in search.news:
                    title = (article.get("title") or "").strip()
                    url = article.get("link") or article.get("url", "")
                    publisher = article.get("publisher") or article.get(
                        "source", "Yahoo Finance"
                    )
                    published_at = (
                        article.get("providerPublishTime")
                        and datetime.datetime.fromtimestamp(
                            article["providerPublishTime"], tz=datetime.timezone.utc
                        ).isoformat()
                        or now_iso
                    )

                    if title and url and not any(n["url"] == url for n in news_items):
                        display_time = _format_published_at(published_at)
                        news_items.append(
                            {
                                "title": title,
                                "url": url,
                                "publisher": publisher,
                                "published_at": published_at,
                                "display_time": display_time,
                                "asset": "Mercados",
                                "asset_color": "#99907c",
                            }
                        )
        except Exception as e:
            print(f"[Market Service] yfinance news error for '{query}': {e}")
            continue

    return news_items[:max_items]
