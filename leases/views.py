from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .serializer import StateSerializer, RentalSerializer, Rental_StateSerializer, Event_TypeSerializer, Selected_ProductSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import State, Rental, Rental_State, Event_Type, Selected_Product
import math
from datetime import datetime
from django.utils import timezone
from rest_framework import status, generics
# Create your views here.


class Selected_Product_Api(generics.GenericAPIView):
    
    def get(self, request):
        return HttpResponse("productos")
    
    def post(self, request):
        customer = request.data["customer"]
        selectedproducts = request.data["selectedproducts"]
        rental = Rental.objects.create(customer_id = customer)
        for selectedproduct in selectedproducts:
            if Event_Type.objects.filter(name=selectedproduct.get("nameevent")).exists():
                event = Event_Type.objects.get(name=selectedproduct.get("nameevent"))
                fecha_string = selectedproduct.get("date")
                fecha_objeto = datetime.strptime(fecha_string, "%d/%m/%Y").strftime("%Y-%m-%d")

                Selected_Product.objects.create(product_id = selectedproduct.get("product"), event_type_id = event.id, rental_id = rental.id, date = fecha_objeto, detail = selectedproduct.get("detail", None))
            else:
                event = Event_Type.objects.create(name=selectedproduct.get("nameevent"))
                fecha_string = selectedproduct.get("date")
                fecha_objeto = datetime.strptime(fecha_string, "%d/%m/%Y").strftime("%Y-%m-%d")
                Selected_Product.objects.create(product_id = selectedproduct.get("product"), event_type_id = event.id, rental_id = rental.id, date = fecha_objeto, detail = selectedproduct.get("detail", None))
        state = State.objects.get(pk=1)
        new_state = Rental_State.objects.create(state_id= state.id, rental_id = rental.id)
        return Response({"state":"success", "message":"Pre reserva creado con éxito"}, status= status.HTTP_201_CREATED)