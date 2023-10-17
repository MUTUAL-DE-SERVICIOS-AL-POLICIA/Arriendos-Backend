from django.db import models
from leases.models import Rental
from products.models import Rate
from customers.models import Customer_type
# Create your models here.
class Requirement(models.Model):
    requirement_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Requirement_Delivered(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class RateRequirement(models.Model):
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    rate = models.ForeignKey(Rate, on_delete=models.CASCADE)
    customer_type = models.ForeignKey(Customer_type, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)