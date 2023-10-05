from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .serializer import StateSerializer, RentalSerializer, Rental_StateSerializer, Event_TypeSerializer, Selected_ProductSerializer
from .models import State, Rental, Rental_State, Event_Type, Selected_Product
import math
from datetime import datetime
from django.utils import timezone
from rest_framework import status, generics
from django.db.models import Count
# Create your views here.


class Selected_Product_Api(generics.GenericAPIView):
    queryset = Selected_Product.objects.all()
    serializer_class = Selected_ProductSerializer

    def get(self, request):
        all_dates = Selected_Product.objects.values_list('date', flat=True).distinct()
        response_data = {}
        for date in all_dates:
            date_str = date.strftime('%Y-%m-%d')  # Convertir la fecha a cadena
            selected_products = Selected_Product.objects.filter(date=date)
            selected_products_data = []
            for product in selected_products:
                product_data = {
                    'selected_product_id': product.id,
                    'room_id': product.product.room_id,
                    'product_id': product.product.id,
                    'room_name': product.product.room.name,
                    'start_time': product.start_time,
                    'end_time': product.end_time,
                    'event_type_name': product.event_type.name
                }
                selected_products_data.append(product_data)
            response_data[date_str] = selected_products_data
        return Response(response_data)

    def post(self, request):
        customer = request.data["customer"]
        selectedproducts = request.data["selected_products"]
        for selected_product in selectedproducts:
            event_type = selected_product.get("event_type_id", None)
            if event_type is not None:
                try:
                    event = Event_Type.objects.get(pk=event_type)
                except:
                    return Response({"message":f"El tipo de evento no es válido"}, status=status.HTTP_404_NOT_FOUND)
        rental = Rental.objects.create(customer_id = customer)
        for selectedproduct in selectedproducts:
            event_type = selectedproduct.get("event_type_id", None)
            if event_type is not None:
                event = Event_Type.objects.get(pk=event_type)
                date_string = selectedproduct.get("date")
                date_object = datetime.strptime(date_string, "%d/%m/%Y").strftime("%Y-%m-%d")
                start_time = selectedproduct.get("start_time")
                end_time = selectedproduct.get("end_time")
                Selected_Product.objects.create(product_id = selectedproduct.get("product"), event_type_id = event.id, rental_id = rental.id, date = date_object, start_time= start_time, end_time = end_time, detail = selectedproduct.get("detail", None))
            else:
                event = Event_Type.objects.create(name=selectedproduct.get("event_type"))
                date_string = selectedproduct.get("date")
                date_object = datetime.strptime(date_string, "%d/%m/%Y").strftime("%Y-%m-%d")
                start_time = selectedproduct.get("start_time")
                end_time = selectedproduct.get("end_time")
                Selected_Product.objects.create(product_id = selectedproduct.get("product"), event_type_id = event.id, rental_id = rental.id, date = date_object, start_time= start_time, end_time = end_time, detail = selectedproduct.get("detail", None))
        state = State.objects.get(pk=1)
        new_state = Rental_State.objects.create(state_id= state.id, rental_id = rental.id)
        return Response({"state":"success", "message":"Pre reserva creado con éxito"}, status= status.HTTP_201_CREATED)

class Event_Api(generics.ListAPIView):
    queryset = Event_Type.objects.all()
    serializer_class = Event_TypeSerializer