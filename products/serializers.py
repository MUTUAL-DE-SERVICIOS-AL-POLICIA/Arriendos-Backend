from rest_framework import serializers
from .models import Rate, HourRange, Product, Price
from customers.models import Customer_type
from customers.serializer import Customer_typeSerializer

class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        depth = 2
class HourRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourRange
        fields = ['name']
class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'