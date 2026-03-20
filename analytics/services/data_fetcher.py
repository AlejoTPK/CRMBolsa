import yfinance as yf
import pandas as pd
from django.db import transaction
from ..models import Commodity, PriceData

class MarketDataService:
    @staticmethod
    def sync_commodity(symbol, period="1y", interval="1d"):
        try:
            # Quitamos todo lo de 'requests' y 'session'
            # Dejamos que yfinance maneje la conexión internamente
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                print(f"Advertencia: No hay datos para {symbol}")
                return 0

            commodity, _ = Commodity.objects.get_or_create(symbol=symbol)
            
            records_created = 0
            with transaction.atomic():
                for timestamp, row in df.iterrows():
                    obj, created = PriceData.objects.update_or_create(
                        commodity=commodity,
                        timestamp=timestamp,
                        defaults={
                            'open_price': row['Open'],
                            'high_price': row['High'],
                            'low_price': row['Low'],
                            'close_price': row['Close'],
                            'volume': int(row['Volume']),
                        }
                    )
                    if created: records_created += 1
            return records_created
            
        except Exception as e:
            print(f"Error crítico en sync_commodity: {e}")
            raise e