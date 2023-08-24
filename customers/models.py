from django.db import models

# Create your models here.
class Customer_type(models.Model):
    name = models.CharField(max_length=100)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    ci = models.CharField(max_length=30)
    phone = models.CharField(max_length=100)
    date_created = models.DateField(auto_now_add=True)
    customer_type = models.ForeignKey(Customer_type, related_name="customer_types", on_delete=models.CASCADE)
