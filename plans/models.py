from django.db import models

# Create your models here.
class Plan(models.Model):
    plan_name = models.CharField(max_length=150)
    plan_discount = models.FloatField()
    rooms_min = models.IntegerField()
    rooms_max = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plan_name} ({self.rooms_min}-{self.rooms_max} ambientes)"