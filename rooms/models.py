from django.db import models

# Create your models here.
class Property(models.Model):
    name=models.CharField(max_length=250)
    address = models.CharField(max_length=250, null=True)
    department =models.CharField(max_length=100, null=True)
    def get_upload_to(instance, filename):
        return f'property_photos/{filename}'
    photo = models.ImageField(upload_to=get_upload_to)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']

class Room(models.Model):
    property=models.ForeignKey(Property, on_delete=models.CASCADE)
    name=models.CharField(max_length=250)
    capacity=models.IntegerField()
    warranty=models.FloatField()
    is_active = models.BooleanField(default=True)
    group = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.property})"


class Sub_Room(models.Model):
    STATE_CHOICES = [
        ('BUENO', 'Bueno'),
        ('REGULAR', 'Regular'),
        ('MALO', 'Malo'),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    quantity = models.IntegerField(null=True)
    state = models.CharField(max_length=250, choices=STATE_CHOICES, default='BUENO')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.room}"