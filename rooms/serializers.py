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
class RoomsSerializer(serializers.ModelSerializer):
    sub_environments = serializers.SerializerMethodField()
    property = PropertySerializer()
    class Meta:
        model = Room
        fields = '__all__'
    def get_sub_environments(self,obj):
        sub_environments = Sub_Environment.objects.filter(room_id = obj)
        sub_environments_serializer = Sub_EnvironmentSerializer(sub_environments, many=True)
        return sub_environments_serializer.data