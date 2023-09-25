from django.contrib.auth.models import User
from .models import Room
from rooms.serializers import RoomSerializer
from .models import Assign
from rest_framework import serializers

class UserCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active')


class AssignSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Assign
        fields = '__all__'
class AssignsSerializer(serializers.ModelSerializer):
    user = UserCustomSerializer()
    room = RoomSerializer()
    class Meta:
        model = Assign
        fields = '__all__'