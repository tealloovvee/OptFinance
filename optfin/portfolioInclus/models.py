from django.db import models

class PortfolioComposition(models.Model):
    id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    trading_pair = models.ForeignKey(CryptoCoin, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.portfolio} - {self.trading_pair}"
