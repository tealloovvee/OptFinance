from django.db import models
from portfolios.models import Portfolio
from cryptocurrencies.models import CryptoCoin

class PortfolioComposition(models.Model):
    id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    weight = models.JSONField(default=dict)
    name = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.portfolio} - {self.trading_pair}"
