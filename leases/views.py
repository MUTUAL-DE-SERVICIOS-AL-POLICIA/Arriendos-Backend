from django.shortcuts import render
from rest_framework.response import Response
from .serializer import Event_TypeSerializer, Selected_ProductSerializer, StateSerializer, Additional_hour_AppliedSerializer
from .models import State, Rental, Event_Type, Selected_Product, Additional_Hour_Applied
from customers.models import Customer,Contact
from customers.serializer import CustomersSerializer
from products.models import Product, Price
from requirements.models import Requirement_Delivered
from plans.models import Plan
from financials.models import Warranty_Movement, Payment
from datetime import datetime
import pytz
from rest_framework import status, generics
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from Arriendos_Backend.util import required_fields
from .function import Make_Delivery_Form, Make_Overtime_Form
from .permissions import *
from rest_framework.permissions import IsAuthenticated

class StateRentalListCreateView(generics.ListCreateAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticated, HasViewRentalStatePermission, HasAddRentalStatePermission]
    def get_permissions(self):
        if self.request.method == 'POST':
            return [HasAddRentalStatePermission()]
        if self.request.method == 'GET':
            return [HasViewRentalStatePermission()]

rental = openapi.Parameter('rental', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
class Get_Rental(generics.ListCreateAPIView):
    @swagger_auto_schema(
    operation_description="API para obtener la información de cada arriendo",
    manual_parameters=[rental],
    )
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
    permission_classes = [IsAuthenticated, HasViewRentalStatePermission, HasAddRentalStatePermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewRentalStatePermission()]
    @swagger_auto_schema(
    operation_description="Listado de los estados de los arriendos",
    manual_parameters=[rental],
    )
    def get (self, request):
        list= State.objects.all().order_by('id')
        states=[]
        for state in list:
            if len(state.next_state) > 0:
                item={
                    "id":state.id,
                    "name":state.name
                }
                states.append(item)
        return Response(states)

room = openapi.Parameter('room', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
class Selected_Product_Calendar_Api(generics.GenericAPIView):
    queryset = Selected_Product.objects.all()
    serializer_class = Selected_ProductSerializer
    permission_classes = [IsAuthenticated, HasViewSelectedProductPermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewSelectedProductPermission()]
    @swagger_auto_schema(
    operation_description="API de los productos seleccionados para el calendario y por ambiente",
    manual_parameters=[room],
    )
    def get(self, request, *args, **kwargs):
        room = request.GET.get('room', None)
        if room is None:
            all_dates = Selected_Product.objects.values_list('start_time', flat=True).distinct().order_by('id')
            date_products = []
            for date in all_dates:
                selected_products = Selected_Product.objects.filter(start_time=date)
                for product in selected_products:
                    if product.rental.state_id < 6:
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
                if product.rental.state_id < 6:
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

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'start_time': openapi.Schema(type=openapi.TYPE_STRING),
        'end_time': openapi.Schema(type=openapi.TYPE_STRING),
    }
)
class Selected_Product_Detail(generics.GenericAPIView):
    queryset = Selected_Product.objects.all()
    serializer_class = Selected_ProductSerializer
    permission_classes = [IsAuthenticated, HasViewSelectedProductPermission]
    def get_permissions(self):
        print(self.request.user.get_all_permissions())
        if self.request.method == 'PATCH':
            return [HasChangeSelectedProductPermission()]
    def get_selected_product(self, pk):
        try:
            return Selected_Product.objects.get(pk=pk)
        except:
            return None

    def get(self, pk):
        selected_product = self.get_selected_product(pk=pk)
        if selected_product == None:
            return Response({"error":"no se ha encontrado el producto seleccionado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(selected_product)
        return Response({"data": {"selected_product":serializer.data}}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
    operation_description="Cambiar fecha de producto seleccionado",
    request_body=request_body_schema
    )
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

contact_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'ci_nit': openapi.Schema(type=openapi.TYPE_STRING),
        'phone': openapi.Schema(type=openapi.TYPE_STRING),
        'degree': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

selected_product_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'product': openapi.Schema(type=openapi.TYPE_INTEGER),
        'event_type': openapi.Schema(type=openapi.TYPE_STRING),
        'start_time': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'end_time': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'detail': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customer': openapi.Schema(type=openapi.TYPE_INTEGER),
        'plan': openapi.Schema(type=openapi.TYPE_INTEGER),
        'selected_products': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=selected_product_schema
        ),
    }
)

class Pre_Reserve_Api(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HasAddRentalPermission]
    def get_permissions(self):
        if self.request.method == 'POST':
            return [HasAddRentalPermission() ]
    @swagger_auto_schema(
    operation_description="Pre reserva de arriendos, si es plan se envian mas de un producto seleccionado",
    request_body=request_body_schema
    )
    def post(self, request):
        customer = request.data["customer"]
        try:
            Customer.objects.get(pk=customer)
        except:
            return Response({"error": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        selected_products = request.data["selected_products"]
        for selected_product in selected_products:
            event_type = selected_product.get("event_type", None)
            if event_type != "":
                try:
                    event = Event_Type.objects.filter(name=event_type)
                except:
                    return Response({"error":f"El tipo de evento no es válido"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "El tipo de evento no es válido"}, status=status.HTTP_404_NOT_FOUND)
        first_year = timezone.datetime.strptime(selected_products[0]['start_time'], '%Y-%m-%dT%H:%M:%S.%fZ').year
        for selected_product in selected_products:
                product = selected_product.get("product")
                start_time = selected_product.get("start_time")
                try:
                    product = Product.objects.get(pk=product)
                    start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                    if (start_time.year > first_year):
                        return Response({"error":"Las fechas no estan en la misma gestión"}, status=status.HTTP_404_NOT_FOUND)
                except:
                    return Response({"error":"el producto no es válido o la fecha no es correcta"}, status=status.HTTP_404_NOT_FOUND)
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

rental = openapi.Parameter('rental', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
class Get_state(generics.ListAPIView):
    permission_classes = [IsAuthenticated, HasViewRentalPermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewRentalPermission() ]
    @swagger_auto_schema(
    operation_description="API del estado de arriendo y siguiente estado",
    manual_parameters=[rental],
    )
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

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'rental': openapi.Schema(type=openapi.TYPE_INTEGER),
        'state': openapi.Schema(type=openapi.TYPE_INTEGER)
    }
)
class Change_state(generics.ListAPIView):
    permission_classes = [IsAuthenticated, HasChangeRentalPermission]
    def get_permissions(self):
        if self.request.method == 'POST':
            return [HasChangeRentalPermission() ]
    def prereserved(self, rental_id,state):
        if self.validated_state(rental_id, state):
            state_obj = State.objects.get(pk=state)
            self.save_state(rental_id,state_obj)
            response_data = {
                "message": f"cambio de estado a {state_obj.name} exitosamente"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({"error": "No se puede cambiar de estado "}, status=status.HTTP_400_BAD_REQUEST)
    def reserved(self, rental_id, state):
        state_obj = State.objects.get(pk=state)
        requirement_delivered = Requirement_Delivered.objects.filter(rental_id=rental_id)
        if self.validated_state(rental_id, state):
            if requirement_delivered.exists():
                self.save_state(rental_id,state_obj)
                response_data = {
                    "message": f"cambio de estado a {state_obj.name} exitosamente"
                }
                return Response(response_data, status=status.HTTP_200_OK)
            return Response({"error": "No existen requisitos entregados"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "No se puede cambiar de estado "}, status=status.HTTP_400_BAD_REQUEST)
    def rented(self, rental_id, state):
        state_obj = State.objects.get(pk=state)
        warranty = Warranty_Movement.objects.filter(rental_id=rental_id)
        if self.validated_state(rental_id, state):
            if not warranty.exists():
                return Response({"error": "No se puede realizar la acción, no tiene garantías registradas"}, status=status.HTTP_400_BAD_REQUEST)
            payment = Payment.objects.filter(rental_id=rental_id)
            if not payment.exists():
                return Response({"error": "No se puede realizar la acción, no tiene pagos registrados"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                last_payment = payment.latest("id")
                if last_payment.payable_mount == 0:
                    self.save_state(rental_id,state_obj)
                    response_data = {
                        "message": f"cambio de estado a {state_obj.name} exitosamente"
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                return Response({"error": f"No se puede realizar la acción, el monto pendiente de pago es: {last_payment.payable_mount}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "No se puede cambiar de estado "}, status=status.HTTP_400_BAD_REQUEST)
    def concluded(self, rental_id, state):
        state_obj = State.objects.get(pk=state)
        last_warranty = Warranty_Movement.objects.filter(rental_id=rental_id).latest("id")
        if self.validated_state(rental_id, state):
            if last_warranty.returned>0:
                self.save_state(rental_id,state_obj)
                response_data = {
                        "message": f"cambio de estado a {state_obj.name} exitosamente"
                    }
                return Response(response_data, status=status.HTTP_200_OK)
            return Response({"error": f"No se puede realizar la acción, la monto de garantía: {last_warranty.balance} no ha sido retornada: "}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "No se puede cambiar de estado "}, status=status.HTTP_400_BAD_REQUEST)
    def canceled(self, rental_id, state):
        state_obj = State.objects.get(pk=state)
        if self.validated_state(rental_id, state):
            self.save_state(rental_id,state_obj)
            response_data = {
                "message": f"cambio de estado a {state_obj.name} exitosamente"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({"error": "No se puede cambiar de estado "}, status=status.HTTP_400_BAD_REQUEST)
    def default_case(self, rental_id, state):
        return Response({"error": "No existe el estado"}, status=status.HTTP_400_BAD_REQUEST)
    def validated_state(self,rental_id,state):
        list_states= Rental.objects.get(pk=rental_id).state.next_state
        for state_object in list_states:
            if state==state_object:
                return True
        return False
    def save_state(self,rental_id, state):
        rental= Rental.objects.get(pk=rental_id)
        rental.state = state
        rental.save()
    @swagger_auto_schema(
    operation_description="Cambiar estado del arriendo",
    request_body=request_body_schema
    )
    def post(self, request):
        validated_fields = ["rental", "state"]
        error_message = required_fields(request, validated_fields)
        if error_message:
            return Response(error_message, status=400)

        rental_id = request.data["rental"]
        try:
            state = request.data["state"]
            rental = Rental.objects.get(pk=rental_id)
            switcher = {
                '1': self.prereserved,
                '2': self.reserved,
                '3': self.rented,
                '4': self.concluded,
                '5': self.canceled
            }
            opcion = f"{state}"
            response = switcher.get(opcion, self.default_case)(rental_id,state)
            return response
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'rental': openapi.Schema(type=openapi.TYPE_INTEGER),
        'product': openapi.Schema(type=openapi.TYPE_INTEGER)
    }
)
class Delivery_Form(generics.GenericAPIView):

    @swagger_auto_schema(
    operation_description="API  de formulario de entrega y recepción de ambientes, con rental y producto seleccionado",
    request_body=request_body_schema
    )
    def post(self, request, *args, **kwargs):
        rental = int(request.data["rental"])
        selected_product = int(request.data["product"])
        if rental is None:
            return Response({"error": "No se ha enviado rental"}, status=status.HTTP_404_NOT_FOUND)
        if selected_product is None:
            return Response({"error": "No se ha enviado selected_product"}, status=status.HTTP_404_NOT_FOUND)
        return Make_Delivery_Form(request, rental, selected_product)

selected_product = openapi.Parameter('selected_product', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'selected_product': openapi.Schema(type=openapi.TYPE_INTEGER),
        'number': openapi.Schema(type=openapi.TYPE_INTEGER),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'voucher_number': openapi.Schema(type=openapi.TYPE_STRING),
        'price': openapi.Schema(type=openapi.TYPE_INTEGER)
    }
)
class Register_additional_hour_applied(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = Additional_Hour_Applied

    @swagger_auto_schema(
    operation_description="Registrar hora adicional al producto seleccionado",
    request_body=request_body_schema
    )
    def post(self, request):
        selected_product_id = request.data.get('selected_product')
        rental = Selected_Product.objects.get(pk=selected_product_id)
        rental = rental.rental_id
        number = request.data.get('number')
        description = request.data.get('description')
        voucher_number = request.data.get('voucher_number')
        price = request.data.get('price')
        total = number*price
        data= {
            'selected_product': selected_product_id,
            'number': number,
            'description': description,
            'voucher_number': voucher_number,
            'total': total
        }
        data_serialized = Additional_hour_AppliedSerializer(data=data)
        if data_serialized.is_valid():
            data_serialized.save()
            return Make_Overtime_Form(request, rental, selected_product_id, number, price, total, description)
        else:
            return Response({"error":"no se pudo registar la hora extra"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
    operation_description="Horas adicionales aplicadas",
    manual_parameters=[selected_product],
    )
    def get (self, request):
        selected_product_id = request.query_params.get('selected_product')
        additional_hour_applieds = Additional_Hour_Applied.objects.filter(selected_product=selected_product_id)
        list_additional_hour_applied=[]
        for additional_hour_applied in additional_hour_applieds:
            additional_hour_applied_data = {
            'selected_product': additional_hour_applied.selected_product_id,
            'number': additional_hour_applied.number,
            'description': additional_hour_applied.description,
            'voucher_number': additional_hour_applied.voucher_number,
            'total': additional_hour_applied.total
            }
            list_additional_hour_applied.append(additional_hour_applied_data)
        return Response(list_additional_hour_applied, status=status.HTTP_200_OK)

    @swagger_auto_schema(
    operation_description="Eliminar registro de horas extra de producto seleccionado",
    )
    def delete(self,request,selected_product_id):
        try:
            Selected_Product.objects.get(pk=selected_product_id)
            additional_hour_applieds= Additional_Hour_Applied.objects.filter(selected_product_id=selected_product_id).exists()
            if (additional_hour_applieds):
                last_additional_hour_applieds = Additional_Hour_Applied.objects.filter(selected_product_id=selected_product_id).latest('id')
                last_additional_hour_applieds.delete()
                return Response({'mensaje': 'Registro eliminado exitosamente'})
            else:
                return Response({"error": "No existen horas adicionales registradas para ese producto seleccionado"}, status=status.HTTP_400_BAD_REQUEST)
        except Selected_Product.DoesNotExist:
            return Response({"error": "El producto seleccionado no existe."}, status=status.HTTP_400_BAD_REQUEST)
rental = openapi.Parameter('rental', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
class List_additional_hour_applied(generics.ListAPIView):
    serializer_class = Additional_Hour_Applied

    @swagger_auto_schema(
    operation_description="Listado de horas adicionales aplicadas",
    manual_parameters=[rental],
    )
    def get (self, request):
        rental_id = request.query_params.get('rental')
        list_selected_product = Selected_Product.objects.filter(rental_id=rental_id)
        try:
            list_additional_hour_applied=[]
            for selected_product in list_selected_product:
                room = selected_product.product.room.name
                property =  selected_product.product.room.property.name
                event = selected_product.event_type.name
                date = selected_product.start_time
                additional_hour_applieds = Additional_Hour_Applied.objects.filter(selected_product=selected_product)
                for additional_hour_applied in additional_hour_applieds:
                    additional_hour_applied_data = {
                    'selected_product': additional_hour_applied.selected_product_id,
                    'number': additional_hour_applied.number,
                    'description': additional_hour_applied.description,
                    'voucher_number': additional_hour_applied.voucher_number,
                    'total': additional_hour_applied.total,
                    'room': room,
                    'property': property,
                    'event': event,
                    'date': date,
                    }
                    list_additional_hour_applied.append(additional_hour_applied_data)
            return Response(list_additional_hour_applied, status=status.HTTP_200_OK)
        except Selected_Product.DoesNotExist:
            return Response({"error": "No existe el arriendo"}, status=status.HTTP_404_NOT_FOUND)