from rest_framework import serializers
from .models import State, Selected_Product, Rental, Event_Type, Additional_Hour_Applied
from products.serializers import RateSerializer
from rooms.serializers import RoomSerializer, RoomsSerializer
from products.models import Product, HourRange
from products.serializers import HourRangeSerializer
from customers.serializer import CustomersSerializer
from financials.models import Payment, Warranty_Movement
from financials.serializer import Payment_Serializer, Warranty_Movement_Serializer
import pytz

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
    room = RoomsSerializer()
    rate = RateSerializer()
    hour_range = HourRangeSerializer()
    ref_name = 'ProductLeases'

    class Meta:
        model = Product
        fields = '__all__'
    def get_hour_range(self, obj):
        hour_ranges = HourRange.objects.filter(id=obj)
        hour_ranges_serializer = HourRangeSerializer(hour_ranges, many = True)
        return hour_ranges_serializer.data

class Selected_ProductSerializer(serializers.ModelSerializer):
     product = ProductSerializer()
     event_type = Event_TypeSerializer()
     rental = RentalSerializer()

     class Meta:
        model = Selected_Product
        fields = '__all__'

month_spanish = {
    'January': 'Enero',
    'February': 'Febrero',
    'March': 'Marzo',
    'April': 'Abril',
    'May': 'Mayo',
    'June': 'Junio',
    'July': 'Julio',
    'August': 'Agosto',
    'September': 'Septiembre',
    'October': 'Octubre',
    'November': 'Noviembre',
    'December': 'Diciembre',
}

class CustomDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        time_zone = pytz.timezone('America/La_Paz')
        normalized_date = value.astimezone(time_zone)
        month = month_spanish[value.strftime('%B')]
        formatted_date = normalized_date.strftime('%d de ') + month + normalized_date.strftime(' de %Y %H:%M %p')
        return formatted_date

    def get_hour_only(self, value):
            time_zone = pytz.timezone('America/La_Paz')
            normalized_date = value.astimezone(time_zone)
            hour_only = normalized_date.strftime('%H:%M %p')
            return hour_only

class Selected_ProductsSerializer(serializers.ModelSerializer):
     product = ProductSerializer()
     event_type = Event_TypeSerializer()
     start_time = CustomDateTimeField(format="%d de %B de %Y %H:%M %p")
     end_time = CustomDateTimeField(format="%d de %B de %Y %H:%M %p")
     start_time_only_hour = serializers.SerializerMethodField()
     end_time_only_hour = serializers.SerializerMethodField()
     additional_hour_applieds = serializers.SerializerMethodField()

     class Meta:
        model = Selected_Product
        fields =  ('id', 'detail', 'event_type', 'start_time', 'end_time', 'product', 'rental', 'product_price', 'start_time_only_hour', 'end_time_only_hour', 'additional_hour_applieds')

     def get_start_time_only_hour(self, obj):
        return CustomDateTimeField().get_hour_only(obj.start_time)

     def get_end_time_only_hour(self, obj):
        return CustomDateTimeField().get_hour_only(obj.end_time)

     def get_additional_hour_applieds(self, obj):
        additional_hour_applieds = Additional_Hour_Applied.objects.filter(selected_product_id=obj).order_by('id')
        serializer = Additional_hour_AppliedSerializer(additional_hour_applieds, many=True)
        return serializer.data
class RentalsSerializer(serializers.ModelSerializer):
    customer = CustomersSerializer()
    state = StateSerializer()
    selected_products = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()
    warranty_movements = serializers.SerializerMethodField()
    class Meta:
        model = Rental
        fields = '__all__'
    def get_selected_products(self, obj):
        selected_products = Selected_Product.objects.filter(rental_id = obj)
        selected_product_serializer = Selected_ProductsSerializer(selected_products, many=True)
        return selected_product_serializer.data
    def get_payments(self, obj):
        payments = Payment.objects.filter(rental_id = obj)
        payment_serializer = Payment_Serializer(payments, many=True)
        return payment_serializer.data
    def get_warranty_movements(self, obj):
        warranty_movements = Warranty_Movement.objects.filter(rental_id = obj)
        warranty_movement_serializer = Warranty_Movement_Serializer(warranty_movements, many=True)
        return warranty_movement_serializer.data
class Additional_hour_AppliedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Additional_Hour_Applied
        fields = '__all__'