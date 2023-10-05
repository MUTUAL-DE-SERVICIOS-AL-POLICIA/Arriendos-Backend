from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .serializer import Event_TypeSerializer, Selected_ProductSerializer
from .models import State, Rental, Rental_State, Event_Type, Selected_Product
import math
from datetime import datetime, time
from django.utils import timezone
from rest_framework import status, generics
from django.db.models import Count
# Create your views here.


class Selected_Product_Api(generics.GenericAPIView):
    queryset = Selected_Product.objects.all()
    serializer_class = Selected_ProductSerializer

    def get(self, request):
        all_dates = Selected_Product.objects.values_list('date', flat=True).distinct()
        date_products = []
        for date in all_dates:
            date_str = date.strftime('%Y-%m-%d')
            selected_products = Selected_Product.objects.filter(date=date)
            
            for product in selected_products:
                start_time = product.start_time
                end_time = product.end_time
                date = product.date.strftime('%Y-%m-%d')
                
                start_date_time = datetime.combine(product.date, start_time)
                end_date_time = datetime.combine(product.date, end_time)

                date_time_format = "%Y-%m-%d %H:%M:%S.%f"
                formatted_start_time = start_date_time.strftime(date_time_format)
                formatted_end_time = end_date_time.strftime(date_time_format)

                product_data = {
                    'selected_product_id': product.id,
                    'room_id': product.product.room_id,
                    'product_id': product.product.id,
                    'room_name': product.product.room.name,
                    'start_time': formatted_start_time,
                    'end_time': formatted_end_time,
                    'date': product.date,
                    'event_type_name': product.event_type.name
                }
                
                date_products.append(product_data)
        return Response(date_products)

    def post(self, request):
        customer = request.data["customer"]
        selected_products = request.data["selected_products"]
        for selected_product in selected_products:
            event_type = selected_product.get("event_type_id", None)
            if event_type is not None:
                try:
                    event = Event_Type.objects.get(pk=event_type)
                except:
                    return Response({"message":f"El tipo de evento no es válido"}, status=status.HTTP_404_NOT_FOUND)
        rental = Rental.objects.create(customer_id = customer)
        for selected_product in selected_products:
            event_type = selected_product.get("event_type_id", None)
            if event_type is not None:
                event = Event_Type.objects.get(pk=event_type)
                start_time = selected_product.get("start_time")
                date_time_obj = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
                date = date_time_obj.date()  #Formato 'YYYY-MM-DD'
                start_time = date_time_obj.time()  #Formato 'HH:MM:SS'
                end_time = selected_product.get("end_time")
                date_time_obj = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S.%f")
                end_time = date_time_obj.time()
                
                Selected_Product.objects.create(product_id = selected_product.get("product"), event_type_id = event.id, rental_id = rental.id, date = date, start_time= start_time, end_time = end_time, detail = selected_product.get("detail", None))
            else:
                event = Event_Type.objects.create(name=selected_product.get("event_type"))
                start_time = selected_product.get("start_time")
                date_time_obj = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
                date = date_time_obj.date()  #Formato 'YYYY-MM-DD'
                start_time = date_time_obj.time()  #Formato 'HH:MM:SS'
                end_time = selected_product.get("end_time")
                date_time_obj = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S.%f")
                end_time = date_time_obj.time()

                Selected_Product.objects.create(product_id = selected_product.get("product"), event_type_id = event.id, rental_id = rental.id, date = date, start_time= start_time, end_time = end_time, detail = selected_product.get("detail", None))
        state = State.objects.get(pk=1)
        new_state = Rental_State.objects.create(state_id= state.id, rental_id = rental.id)
        return Response({"state":"success", "message":"Pre reserva creado con éxito"}, status= status.HTTP_201_CREATED)

class Event_Api(generics.ListAPIView):
    queryset = Event_Type.objects.all()
    serializer_class = Event_TypeSerializer