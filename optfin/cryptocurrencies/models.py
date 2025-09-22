from django.db import models

class CryptoCoin(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    pair = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.pair
