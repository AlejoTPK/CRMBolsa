from django.core.management.base import BaseCommand
from analytics.services.data_fetcher import MarketDataService

class Command(BaseCommand):
    help = 'Sincroniza precios de Oro (Gold) y Petróleo (Crude Oil) desde Yahoo Finance'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Iniciando sincronización de commodities ---"))
        
        # Lista de símbolos de Yahoo Finance: Oro (GC=F) y Petróleo (CL=F)
        commodities = [
            {'symbol': 'GC=F', 'name': 'Gold'},
            {'symbol': 'CL=F', 'name': 'Crude Oil'},
        ]

        for item in commodities:
            self.stdout.write(f"Sincronizando {item['name']} ({item['symbol']})...")
            try:
                # Usamos el servicio que creamos antes
                count = MarketDataService.sync_commodity(item['symbol'], period="1y")
                self.stdout.write(self.style.SUCCESS(f"Hecho: {count} registros nuevos/actualizados para {item['name']}."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error con {item['symbol']}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("--- Proceso completado con éxito ---"))