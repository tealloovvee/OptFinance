from django.db import models
from cryptocurrencies.models import CryptoCoin

class OHLCV(models.Model):
    id = models.AutoField(primary_key=True)
    trading_pair = models.ForeignKey(CryptoCoin, on_delete=models.CASCADE)
    interval = models.CharField(max_length=20)
    open_time = models.DateTimeField()
    open_price = models.DecimalField(max_digits=20, decimal_places=8)
    high_price = models.DecimalField(max_digits=20, decimal_places=8)
    low_price = models.DecimalField(max_digits=20, decimal_places=8)
    close_price = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=30, decimal_places=10)

    def __str__(self):
        return f"{self.trading_pair} {self.interval} {self.open_time}"
