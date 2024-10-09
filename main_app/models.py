from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# class WatchList(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     coin = models.ForeignKey(Coin, on_delete=models.CASCADE)

class Coin(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    price = models.FloatField()
    market_cap = models.FloatField()
    volume = models.FloatField()
    circulating_supply = models.FloatField()
    change = models.FloatField()
    image = models.URLField()
    
    def __str__(self):
        return self.name