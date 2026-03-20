from celery import shared_task
from .services.data_fetcher import MarketDataService

@shared_task(bind=True, max_retries=3)
def update_market_data_task(self):
    symbols = ['GC=F', 'CL=F']
    results = {}
    for symbol in symbols:
        try:
            results[symbol] = MarketDataService.sync_commodity(symbol)
        except Exception as exc:
            raise self.retry(exc=exc, countdown=60)
    return results