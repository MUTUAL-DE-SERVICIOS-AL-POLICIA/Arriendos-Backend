from django.contrib.postgres.fields import ArrayField
from django.db import models
from rooms.models import Room
from customers.models import Customer_type



# Create your models here.

class Rate(models.Model):
    name=models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

class HourRange(models.Model):
    name=models.CharField(max_length=250)

class Product(models.Model):
    rate = models.ForeignKey(Rate,on_delete=models.PROTECT)
    room= models.ForeignKey(Room,on_delete=models.PROTECT)
    hour_range = models.ForeignKey(HourRange,on_delete=models.PROTECT)
    day = ArrayField(models.CharField())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class Price(models.Model):
    product = models.ForeignKey(Product,on_delete=models.PROTECT)
    mount = models.FloatField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)