from django.db import models

# Create your models here.
class Property(models.Model):
    name=models.CharField(max_length=250)
    address = models.CharField(max_length=250, null=True)
    department =models.CharField(max_length=100, null=True)
    def get_upload_to(instance, filename):
        return f'property_photos/{filename}'
    photo = models.ImageField(upload_to=get_upload_to)

class Room(models.Model):
    property=models.ForeignKey(Property, on_delete=models.CASCADE)
    name=models.CharField(max_length=250)
    capacity=models.IntegerField()
    warranty=models.FloatField()
    is_active = models.BooleanField(default=True)
    group = models.CharField(max_length=100)


class Sub_Room(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    quantity = models.IntegerField(null=True)
    state = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)