from django.db import models
from leases.models import Rental, Selected_Product

class Payment(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    voucher_number= models.IntegerField()
    detail = models.CharField(null=True)
    payable_mount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Warranty_Movement (models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    returned = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    detail = models.CharField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Event_Damage (models.Model):
    selected_product = models.ForeignKey(Selected_Product, on_delete=models.CASCADE)
    warranty_movement = models.ForeignKey(Warranty_Movement, on_delete=models.CASCADE)
    mount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)