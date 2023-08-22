from django.db import models
from rooms.models import Room
# Create your models here.

class Rates(models.Model):
    room=models.ForeignKey(Room, on_delete=models.CASCADE)
    name=models.CharField(max_length=250)
class Time(models.Model):
    name=models.CharField(max_length=250)
class Day(models.Model):
    name=models.CharField(max_length=250)
class Product(models.Model):
    rates = models.ForeignKey(Rates,on_delete=models.PROTECT)
    day = models.ForeignKey(Day,on_delete=models.PROTECT)
    time = models.ForeignKey(Time,on_delete=models.PROTECT)
    day = models.ForeignKey(Day,on_delete=models.PROTECT)
    price_time = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
class Prize(models.Model):
    product = models.ForeignKey(Product,on_delete=models.PROTECT)
    mount = models.FloatField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)