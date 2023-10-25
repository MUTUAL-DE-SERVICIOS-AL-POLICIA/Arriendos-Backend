from rest_framework import serializers
from financials.models import Payment, Warranty_Movement

class Payment_Serializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields = '__all__'

class Warranty_Movement_Serializer(serializers.ModelSerializer):
    class Meta:
        model=Warranty_Movement
        fields ='__all__'