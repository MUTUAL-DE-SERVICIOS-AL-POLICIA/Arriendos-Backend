from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse
from .serializer import Event_TypeSerializer, Selected_ProductSerializer, StateSerializer
from .models import State, Rental, Event_Type, Selected_Product
from customers.models import Customer,Contact
from customers.serializer import CustomersSerializer
from products.models import Product, Price
from plans.models import Plan
from datetime import datetime
import pytz
from rest_framework import status, generics
from django.utils import timezone
from Arriendos_Backend.util import required_fields

class StateRentalListCreateView(generics.ListCreateAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
class Get_Rental(generics.ListCreateAPIView):
    def get(sel, request):
        rental_id = request.GET.get('rental', None)
        rental=Rental.objects.get(pk=rental_id)
        customer=rental.customer
        customer_contacts=Contact.objects.filter(customer_id=customer.id)
        contacts=[]
        for customer_contact in customer_contacts:
            customer_contact_data = {
                "name":customer_contact.name,
                "ci_nit":customer_contact.ci_nit,
                "phone":customer_contact.phone
            }
            contacts.append(customer_contact_data)
        customer={
            "institution_name":customer.institution_name,
            "nit":customer.nit,
            "contacts":contacts
        }
        selected_products = Selected_Product.objects.filter(rental=rental_id)
        products=[]
        for selected_product in selected_products:
            product=selected_product.product
            room = product.room
            property=room.property
            product_data={
                "id": selected_product.id,
                "property":property.name,
                "room":room.name,
                "hour_range":product.hour_range.time,
                "start_time":selected_product.start_time,
                "end_time":selected_product.end_time,
                "detail":selected_product.detail,
                "event":selected_product.event_type.name
            }
            products.append(product_data)
        return Response({"customer":customer, "products":products})
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
        
class Selected_Product_Detail(generics.GenericAPIView):
    queryset = Selected_Product.objects.all()
    serializer_class = Selected_ProductSerializer

    def get_selected_product(self, pk):
        try:
            return Selected_Product.objects.get(pk=pk)
        except:
            return None

    def get(self, pk):
        selected_product = self.get_selected_product(pk=pk)
        if selected_product == None:
            return Response({"status":"fail", "message":"no se ha encontrado el producto seleccionado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(selected_product)
        return Response({"status":"success", "data": {"selected_product":serializer.data}}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        selected_product = self.get_selected_product(pk=pk)
        start_time = request.data["start_time"]
        end_time = request.data["end_time"]
        selected_products_data = Selected_Product.objects.filter(rental_id = selected_product.rental_id)
        selected_products_data = selected_products_data.first()
        first_year = selected_products_data.start_time.year
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        start_time = pytz.timezone('America/La_Paz').localize(start_time)
        end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        end_time = pytz.timezone('America/La_Paz').localize(end_time)
        today = datetime.now(pytz.timezone('America/La_Paz'))
        if today > start_time:
            return Response({"message":"La fecha no es válida"}, status=status.HTTP_400_BAD_REQUEST)
        if start_time.year > first_year:
            return Response({"message": "La fecha no es válida"}, status=status.HTTP_404_NOT_FOUND)
        rental = Rental.objects.get(pk= selected_product.rental_id)
        if rental.state_id >3:
            return Response({"message":"No se puede editar una reserva que ya fue confirmada o cancelada"})
        selected_product.start_time = start_time
        selected_product.end_time = end_time
        selected_product.save()
        return Response({"message":"Reserva editada con éxito"}, status=status.HTTP_201_CREATED)

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
        first_year = timezone.datetime.strptime(selected_products[0]['start_time'], '%Y-%m-%dT%H:%M:%S.%fZ').year
        for selected_product in selected_products:
                product = selected_product.get("product")
                start_time = selected_product.get("start_time")
                try:
                    product = Product.objects.get(pk=product)
                    start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                    if (start_time.year > first_year):
                        return Response({"message":"Las fechas no estan en la misma gestión"}, status=status.HTTP_404_NOT_FOUND)
                except:
                    return Response({"message":"el producto no es válido o la fecha no es correcta"}, status=status.HTTP_404_NOT_FOUND)
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
            rental = Rental.objects.create(customer_id = customer, state_id = 1, plan_id = request.data["plan"], initial_total=initial_total)
        else:
            rental = Rental.objects.create(customer_id = customer, state_id = 1, initial_total = initial_total)
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
        return Response({"status":"success", "message": "Pre reserva creada con éxito"}, status=status.HTTP_201_CREATED)

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

class Change_state(generics.ListAPIView):
        def post(self, request):
            validated_fields = ["rental","state"]
            error_message = required_fields(request, validated_fields)
            if error_message:
                return Response(error_message, status=400)
            rental_id = request.data["rental"]
            state = request.data["state"]
            try:
                state = State.objects.get(pk=state)
                rental= Rental.objects.get(pk=rental_id)
                rental.state = state
                rental.save()
                response_data = {
                    "state":"success",
                    "message":f"cambio de estado a {state.name} exitosamente"
                }
                return Response(response_data, status=status.HTTP_200_OK)
            except Rental.DoesNotExist:
                return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)
