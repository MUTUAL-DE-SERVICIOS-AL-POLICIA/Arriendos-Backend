from django.db import models
from customers.models import Customer
from products.models import Product

# Create your models here.
class State(models.Model):
    name = models.CharField(max_length=50)

class Rental(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Rental_State(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Event_Type(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Selected_Product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    event_type = models.ForeignKey(Event_Type, on_delete=models.CASCADE)
    date = models.DateField()
    detail = models.CharField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)






