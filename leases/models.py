from django.db import models
from customers.models import Customer
from products.models import Product
from plans.models import Plan
from django.contrib.postgres.fields import ArrayField
# Create your models here.
class State(models.Model):
    name = models.CharField(max_length=50)
    next_state = ArrayField(models.IntegerField(), default=list)

    def __str__(self):
        return self.name

class Rental(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, null=True, on_delete=models.CASCADE)
    initial_total = models.FloatField(null=True)
    contract_number = models.CharField(max_length=10,null=True)
    warranty_return_request = models.DateTimeField(null=True)
    warranty_returned = models.DateTimeField(null=True)
    cancel_reason = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.contract_number:
            return f"Contrato {self.contract_number}"
        return f"Arriendo #{self.id}"

    class Meta:
        indexes = [
            models.Index(fields=['state', 'customer']),
            models.Index(fields=['customer', 'state']),
        ]

class Event_Type(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Selected_Product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    event_type = models.ForeignKey(Event_Type, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    detail = models.CharField(max_length=255, null=True)
    product_price = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product} - {self.event_type}"

    class Meta:
        indexes = [
            models.Index(fields=['rental', 'product']),
        ]

class Additional_Hour_Applied(models.Model):
    selected_product = models.ForeignKey(Selected_Product, on_delete=models.CASCADE)
    number = models.IntegerField()
    voucher_number = models.CharField(max_length=255)
    business_name=models.CharField(max_length=255)
    nit= models.CharField(max_length=255)
    total = models.FloatField()
    description = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Hora extra #{self.number} - {self.total}Bs"

    class Meta:
        indexes = [
            models.Index(fields=['selected_product']),
        ]