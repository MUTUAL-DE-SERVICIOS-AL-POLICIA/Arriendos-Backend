from rest_framework import serializers
from .models import Property, Room, Sub_Room

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class Sub_RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sub_Room
        fields = '__all__'
class Sub_RoomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sub_Room
        fields = '__all__'
class RoomsSerializer(serializers.ModelSerializer):
    sub_rooms = serializers.SerializerMethodField()
    property = PropertySerializer()
    class Meta:
        model = Room
        fields = '__all__'
    def get_sub_rooms(self,obj):
        sub_rooms = Sub_Room.objects.filter(room_id = obj)
        sub_rooms_serializer = Sub_RoomSerializer(sub_rooms, many=True)
        return sub_rooms_serializer.data