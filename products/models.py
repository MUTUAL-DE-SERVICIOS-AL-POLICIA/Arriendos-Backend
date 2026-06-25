from django.contrib.postgres.fields import ArrayField
from django.db import models
from rooms.models import Room
from customers.models import Customer_type



# Create your models here.

class Rate(models.Model):
    name=models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

class HourRange(models.Model):
    time=models.IntegerField()

class Product(models.Model):
    rate = models.ForeignKey(Rate,on_delete=models.PROTECT)
    room= models.ForeignKey(Room,on_delete=models.PROTECT)
    hour_range = models.ForeignKey(HourRange,on_delete=models.PROTECT)
    day = ArrayField(models.CharField(max_length=255))
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
class Price(models.Model):
    product = models.ForeignKey(Product,on_delete=models.PROTECT)
    mount = models.FloatField()
    is_active = models.BooleanField()
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Price_Additional_Hour(models.Model):
    hourRange = models.ForeignKey(HourRange, on_delete=models.CASCADE)
    room= models.ForeignKey(Room,on_delete=models.PROTECT)
    mount = models.FloatField()
    state = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)