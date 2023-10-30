from rest_framework import serializers
from .models import Property, Room, Sub_Environment

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class Sub_EnvironmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sub_Environment
        fields = '__all__'
class Sub_EnvironmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sub_Environment
        fields = '__all__'