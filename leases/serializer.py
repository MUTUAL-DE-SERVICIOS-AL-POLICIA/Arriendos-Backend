from rest_framework import serializers
from .models import State, Selected_Product, Rental, Event_Type, Rental_State

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class Rental_StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental_State
        fields = '__all__'

class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = '__all__'

class Event_TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event_Type
        fields = '__all__'

class Selected_ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Selected_Product
        fields = '__all__'

