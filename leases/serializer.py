from rest_framework import serializers
from .models import State, Selected_Product, Rental, Event_Type, Payment
from products.serializers import RateSerializer
from rooms.serializers import RoomSerializer
from products.models import Product

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = '__all__'

class Event_TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event_Type
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    room = RoomSerializer()
    rate = RateSerializer()

    class Meta:
        model = Product
        fields = '__all__'
class Selected_ProductSerializer(serializers.ModelSerializer):
     product = ProductSerializer()
     event_type = Event_TypeSerializer()
     rental = RentalSerializer()

     class Meta:
        model = Selected_Product
        fields = '__all__'

class Payment_Serializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields = '__all__'