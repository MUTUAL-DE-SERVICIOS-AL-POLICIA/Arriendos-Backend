from rest_framework import serializers
from .models import Customer, Customer_type

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        
class Customer_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer_type
        fields = '__all__'