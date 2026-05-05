import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_finnhub():
    api_key = os.getenv("FINNHUB_API_KEY")
    uri = f"wss://ws.finnhub.io?token={api_key}"
    symbols = ["OANDA:XAU_USD", "OANDA:WTICO_USD", "BINANCE:BTCUSDT"]
    print("Connecting to Finnhub WebSocket...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Subscribing...")
            for symbol in symbols:
                await websocket.send(json.dumps({"type": "subscribe", "symbol": symbol}))
                print(f"Subscribed to {symbol}")
            
            # Listen for 10 seconds or until we get 3 messages
            count = 0
            while count < 3:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5)
                    print("Received:", message)
                    count += 1
                except asyncio.TimeoutError:
                    print("Timeout waiting for message (no data yet).")
                    break
    except Exception as e:
        print("WebSocket Error:", e)

asyncio.run(test_finnhub())
