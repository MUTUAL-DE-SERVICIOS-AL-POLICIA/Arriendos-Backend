from django.db import models

class Customer_type(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_institution = models.BooleanField(default=True)
    is_police = models.BooleanField(default=False)
class Customer(models.Model):
    customer_type = models.ForeignKey(Customer_type, related_name="customer_types", on_delete=models.CASCADE)
    institution_name = models.CharField(max_length=255, null=True)
    nit = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Contact(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    degree = models.CharField(max_length=50, null=True)
    nup = models.IntegerField(null=True)
    name = models.CharField(max_length=100)
    ci_nit = models.CharField(max_length=30, null=True)
    phone = models.CharField(max_length=50)
    is_customer = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)