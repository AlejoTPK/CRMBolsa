from django.db import models
from django.core.validators import MinValueValidator

class Commodity(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20, unique=True)  # Ejemplo: 'GC=F'
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Commodities"

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class PriceData(models.Model):
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='prices')
    timestamp = models.DateTimeField()
    open_price = models.DecimalField(max_digits=14, decimal_places=4)
    high_price = models.DecimalField(max_digits=14, decimal_places=4)
    low_price = models.DecimalField(max_digits=14, decimal_places=4)
    close_price = models.DecimalField(max_digits=14, decimal_places=4)
    volume = models.BigIntegerField(validators=[MinValueValidator(0)])

    class Meta:
        # Esto hace que las búsquedas por fecha y commodity sean ultra rápidas
        indexes = [
            models.Index(fields=['commodity', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        unique_together = ('commodity', 'timestamp') # Evita datos duplicados
        ordering = ['-timestamp']