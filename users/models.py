from django.db import models
from rooms.models import Room
from django.contrib.auth.models import User

# Create your models here.
class Assign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Record (models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.TextField()
    model = models.TextField()
    detail = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)