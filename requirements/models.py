from django.db import models
from plans.models import Plan
from products.models import Rate
# Create your models here.
class Requirement(models.Model):
    requirement_name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PlanRequirement(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class RateRequirement(models.Model):
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    rate = models.ForeignKey(Rate, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)