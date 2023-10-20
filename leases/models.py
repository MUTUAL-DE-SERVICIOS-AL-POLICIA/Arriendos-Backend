from django.db import models
from customers.models import Customer
from products.models import Product
from plans.models import Plan
from django.contrib.postgres.fields import ArrayField
# Create your models here.
class State(models.Model):
    name = models.CharField(max_length=50)
    next_state = ArrayField(models.IntegerField(), default=list)

class Rental(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    is_plan=models.BooleanField(default=False)
    plan = models.ForeignKey(Plan, null=True, on_delete=models.CASCADE)
    initial_total = models.FloatField(null=True)
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
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    detail = models.CharField(null=True)
    product_price = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    voucher_number= models.IntegerField()
    detail = models.CharField(null=True)
    payable_mount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
