from rest_framework import serializers
from .models import Rate, HourRange, Product, Price, Price_Additional_Hour
from customers.models import Customer_type
from customers.serializer import Customer_typeSerializer

class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = '__all__'
class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
    @classmethod
    def get_active_price(self, product):
        active_price = product.price_set.filter(is_active=True).first()
        if active_price:
            return {
                'id': active_price.id,
                'mount': active_price.mount,
                'is_active': active_price.is_active,
            }
        else:
            return None
class ProductPrice(serializers.ModelSerializer):
    Product=ProductSerializer()
    Price=PriceSerializer()

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        depth = 2
class HourRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourRange
        fields = '__all__'
class PriceAdditionalHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price_Additional_Hour
        fields = '__all__'