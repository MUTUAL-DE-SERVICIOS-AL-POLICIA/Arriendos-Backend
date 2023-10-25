from rest_framework import serializers
from financials.models import Payment, Warranty_Movement,Event_Damage

class Payment_Serializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields = '__all__'

class Warranty_Movement_Serializer(serializers.ModelSerializer):
    class Meta:
        model=Warranty_Movement
        fields ='__all__'
class Event_Damage_Serializer(serializers.ModelSerializer):
    class Meta:
        model=Event_Damage
        fields ='__all__'