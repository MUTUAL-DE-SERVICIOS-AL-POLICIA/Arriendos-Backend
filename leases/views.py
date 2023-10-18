from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse
from .serializer import Event_TypeSerializer, Selected_ProductSerializer, StateSerializer
from .models import State, Rental, Event_Type, Selected_Product
from customers.models import Customer
from customers.serializer import CustomersSerializer
from products.models import Product, Price
from requirements.models import Requirement_Delivered, Requirement
from plans.models import Plan
from datetime import datetime
import pytz
from rest_framework import status, generics
from django.utils import timezone
from Arriendos_Backend.util import required_fields

class StateRentalListCreateView(generics.ListCreateAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
class List_state(generics.GenericAPIView):
    def get (self, request):
        list= State.objects.all()
        states=[]
        for state in list:
            if len(state.next_state) > 0:
                item={
                    "id":state.id,
                    "name":state.name
                }
                states.append(item)
        return Response(states)

class Selected_Product_Calendar_Api(generics.GenericAPIView):
    queryset = Selected_Product.objects.all()
    serializer_class = Selected_ProductSerializer

    def get(self, request, *args, **kwargs):
        room = request.GET.get('room', None)
        if room is None:
            all_dates = Selected_Product.objects.values_list('start_time', flat=True).distinct().order_by('id')
            date_products = []
            for date in all_dates:
                selected_products = Selected_Product.objects.filter(start_time=date)
                for product in selected_products:
                    customer = Customer.objects.get(pk=product.rental.customer_id)
                    customer_serializer = CustomersSerializer(customer)
                    serialized_customer_data = customer_serializer.data
                    contacts = serialized_customer_data.get("contacts")
                    start_time = timezone.localtime(product.start_time)
                    end_time = timezone.localtime(product.end_time)
                    product_data = {
                        'selected_product_id': product.id,
                        'room_id': product.product.room_id,
                        'product_id': product.product.id,
                        'room_name': product.product.room.name,
                        'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'end_time': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'rental': product.rental.id,
                        'customer_id': product.rental.customer_id,
                        'institution_name': serialized_customer_data["institution_name"],
                        'nit': serialized_customer_data["nit"],
                        'contacts': contacts,
                        'event_type_name': product.event_type.name
                    }

                    date_products.append(product_data)
            return Response(date_products)
        else:
            selected_products = Selected_Product.objects.filter(product__room_id=room)
            date_products = []
            for product in selected_products:
                    customer = Customer.objects.get(pk=product.rental.customer_id)
                    customer_serializer = CustomersSerializer(customer)
                    serialized_customer_data = customer_serializer.data
                    contacts = serialized_customer_data.get("contacts")
                    start_time = timezone.localtime(product.start_time)
                    end_time = timezone.localtime(product.end_time)
                    product_data = {
                        'selected_product_id': product.id,
                        'room_id': product.product.room_id,
                        'product_id': product.product.id,
                        'room_name': product.product.room.name,
                        'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'end_time': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'rental': product.rental.id,
                        'customer_id': product.rental.customer_id,
                        'institution_name': serialized_customer_data["institution_name"],
                        'nit': serialized_customer_data["nit"],
                        'contacts': contacts,
                        'event_type_name': product.event_type.name
                    }
                    date_products.append(product_data)
            return Response(date_products)

class Pre_Reserve_Api(generics.GenericAPIView):

    def post(self, request):
        customer = request.data["customer"]
        try:
            Customer.objects.get(pk=customer)
        except:
            return Response({"message": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        selected_products = request.data["selected_products"]
        for selected_product in selected_products:
            event_type = selected_product.get("event_type", None)
            if event_type != "":
                try:
                    event = Event_Type.objects.filter(name=event_type)
                except:
                    return Response({"message":f"El tipo de evento no es válido"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message": "El tipo de evento no es válido"}, status=status.HTTP_404_NOT_FOUND)
        for selected_product in selected_products:
                product = selected_product.get("product")
                try:
                    product = Product.objects.get(pk=product)
                except:
                    return Response({"message":"el producto no es válido"}, status=status.HTTP_404_NOT_FOUND)
        initial_total = 0
        for selected_product in selected_products:
            product_id = selected_product.get("product")
            product_price = Price.objects.get(product_id = product_id)
            product_price = product_price.mount
            initial_total = initial_total + product_price
        productos_plan = len(selected_products)
        if productos_plan > 1:
            plan_discount = Plan.objects.get(pk=request.data["plan"])
            initial_total = initial_total - (initial_total*(plan_discount.plan_discount/100))
            rental = Rental.objects.create(customer_id = customer, is_plan = True, state_id = 1, plan_id = request.data["plan"], initial_total=initial_total)
        else:
            rental = Rental.objects.create(customer_id = customer, is_plan = False, state_id = 1, initial_total = initial_total)
        for selected_product in selected_products:
            event_type = selected_product.get("event_type")
            product_id = selected_product.get("product")
            product_price = Price.objects.get(product_id = product_id)
            product_price = product_price.mount
            if Event_Type.objects.filter(name=event_type).exists():
                event = Event_Type.objects.get(name=event_type)
                start_time = selected_product.get("start_time")
                start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                start_time = pytz.timezone('America/La_Paz').localize(start_time)
                end_time = selected_product.get("end_time")
                end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                end_time = pytz.timezone('America/La_Paz').localize(end_time)
                Selected_Product.objects.create(product_id = selected_product.get("product"), event_type_id = event.id, rental_id = rental.id, start_time= start_time, end_time = end_time, detail = selected_product.get("detail", None), product_price = product_price)
            else:
                event = Event_Type.objects.create(name=selected_product.get("event_type"))
                start_time = selected_product.get("start_time")
                start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                start_time = pytz.timezone('America/La_Paz').localize(start_time)
                end_time = selected_product.get("end_time")
                end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                end_time = pytz.timezone('America/La_Paz').localize(end_time)
                Selected_Product.objects.create(product_id = selected_product.get("product"), event_type_id = event.id, rental_id = rental.id, start_time= start_time, end_time = end_time, detail = selected_product.get("detail", None), product_price = product_price)
        return Response({"state":"success", "message":"Pre reserva creado con éxito"}, status= status.HTTP_201_CREATED)

class Event_Api(generics.ListAPIView):
    queryset = Event_Type.objects.all()
    serializer_class = Event_TypeSerializer
class Get_state(generics.ListAPIView):
    def get(self, request):
        rental_id = request.query_params.get('rental')
        if not rental_id:
            return Response({"error": "Parámetro 'rental' faltante en la consulta."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            rental = Rental.objects.get(pk=rental_id)
            current_state = rental.state_id
            state = State.objects.get(pk=current_state)
            current_states = {
                "id":state.id,
                "name":state.name
                }
            next_possible_states_id = state.next_state
            next_possible_states=[]
            for next_possible_state in next_possible_states_id:
                state = State.objects.get(pk=next_possible_state)
                next_state = {
                    "id":state.id,
                    "name":state.name
                }
                next_possible_states.append(next_state)
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)
        response_data = {
            "current_state": current_states,
            "next_states": next_possible_states,
        }
        return Response(response_data, status=status.HTTP_200_OK)

class Change_state_to_reserved(generics.ListAPIView):
        def post(self, request):
            validated_fields1 = ["rental","list_requirements"]
            error_message = required_fields(request, validated_fields1)
            if error_message:
                return Response(error_message, status=400)
            rental_id = request.data["rental"]
            list_requirements = request.data["list_requirements"]
            try:
                if list_requirements:
                    rental = Rental.objects.get(pk=rental_id)
                    for requirement in list_requirements:
                        requirement_delivered = Requirement_Delivered()
                        requirement_register=Requirement.objects.get(pk=requirement)
                        requirement_delivered.rental = rental
                        requirement_delivered.requirement = requirement_register
                        requirement_delivered.save()
                    state = State.objects.get(pk=2)
                    rental.state = state
                    rental.save()
                    response_data = {
                        "state":"success",
                        "message":"cambio de estado a Reserva exitosamente"
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
            except Rental.DoesNotExist:
                    return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)