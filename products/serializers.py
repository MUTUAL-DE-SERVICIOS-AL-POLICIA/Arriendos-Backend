from rest_framework import serializers
from .models import Rate, HourRange, Product, Price, Price_Additional_Hour
from customers.models import Customer_type
from customers.serializer import Customer_typeSerializer
from rooms.serializers import RoomLightSerializer

class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = '__all__'

class HourRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourRange
        fields = '__all__'

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'

class PriceHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Price
        fields = ['id', 'product', 'product_name', 'mount', 'is_active', 'valid_from', 'valid_to', 'created_at']
    
    def get_product_name(self, obj):
        if obj.product:
            return f"{obj.product.room.name} - {obj.product.rate.name}"
        return None

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        ref_name = 'ProductProduct'
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

class ProductListSerializer(serializers.ModelSerializer):
    """Serializador optimizado para listar productos"""
    rate_name = serializers.CharField(source='rate.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    property_name = serializers.CharField(source='room.property.name', read_only=True)
    hour_range_time = serializers.IntegerField(source='hour_range.time', read_only=True)
    mount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'rate_name', 'room_name', 'property_name', 'hour_range_time', 'day', 'mount']

    def get_mount(self, obj):
        cache = getattr(obj, '_prefetched_objects_cache', None)
        if cache and 'price_set' in cache:
            active_price = next((p for p in cache['price_set'] if p.is_active), None)
            if active_price:
                return active_price.mount
        return None


class ProductsSerializer(serializers.ModelSerializer):
    room = RoomLightSerializer()
    rate = RateSerializer()
    hour_range = HourRangeSerializer()
    mount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'rate', 'room', 'hour_range', 'day', 'is_deleted', 'created_at', 'updated_at', 'mount']

    def get_mount(self, obj):
        cache = getattr(obj, '_prefetched_objects_cache', None)
        if cache and 'price_set' in cache:
            active_price = next((p for p in cache['price_set'] if p.is_active), None)
            if active_price:
                return active_price.mount
        return None

class PriceAdditionalHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price_Additional_Hour
        fields = '__all__'