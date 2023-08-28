from django.contrib.auth.models import User
from .models import Room
from rooms.serializers import RoomSerializer
from .models import Assing
from rest_framework import serializers

class UserCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class AssingSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Assing
        fields = '__all__'
class AssingsSerializer(serializers.ModelSerializer):
    user = UserCustomSerializer()
    room = RoomSerializer()
    class Meta:
        model = Assing
        fields = '__all__'