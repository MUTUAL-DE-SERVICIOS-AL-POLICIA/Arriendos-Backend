from rest_framework import serializers
from .models import Customer, Customer_type

class Customer_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer_type
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    #customer_type = Customer_typeSerializer()
    class Meta:
        model = Customer
        fields = '__all__'

class CustomersSerializer(serializers.ModelSerializer):
    customer_type = Customer_typeSerializer()
    class Meta:
        model = Customer
        fields = '__all__'
        
        
