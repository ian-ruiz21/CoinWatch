from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Coin(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    price = models.FloatField()
    market_cap = models.FloatField()
    volume = models.FloatField()
    change = models.FloatField()
    image = models.URLField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['price']


class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.ManyToManyField(Coin, related_name="watchlist")
    notes = models.TextField(null=True, blank=True)
    priority = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="low",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
