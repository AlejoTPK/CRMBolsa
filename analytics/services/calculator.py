import pandas as pd
import pandas_ta as ta
from ..models import PriceData

class AnalyticsService:
    @staticmethod
    def get_technical_indicators(commodity_symbol, days=250):
        # Traemos los datos de la DB
        prices = PriceData.objects.filter(
            commodity__symbol=commodity_symbol
        ).order_by('timestamp')
        
        if not prices.exists():
            return []

        # Convertimos a DataFrame de Pandas
        df = pd.DataFrame(list(prices.values('timestamp', 'open_price', 'high_price', 'low_price', 'close_price')))
        df['close_price'] = df['close_price'].astype(float)
        
        # Cálculos con Pandas-TA
        df['SMA_50'] = ta.sma(df['close_price'], length=50)
        df['RSI_14'] = ta.rsi(df['close_price'], length=14)
        
        # Limpiamos valores NaN para que JSON no de error
        df = df.fillna(0)
        
        return df.tail(100).to_dict('records')