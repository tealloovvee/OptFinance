from django.db import models

class Exchange(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    trading_volume = models.DecimalField(max_digits=30, decimal_places=10)
    coins_listed = models.IntegerField()
    rating = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.name
