from django.shortcuts import render
from rest_framework.response import Response
from .serializer import CustomerSerializer, Customer_typeSerializer, CustomersSerializer
from .models import Customer, Customer_type, Contact
import math
from rest_framework import status, generics
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .permissions import *
from rest_framework.permissions import IsAuthenticated
from threadlocals.threadlocals import set_thread_variable
import requests
from django.conf import settings
import re

class Customer_Type_Api(generics.GenericAPIView):
    serializer_class = Customer_typeSerializer
    queryset = Customer_type.objects.all()
    permission_classes = [IsAuthenticated, HasViewCustomerTypePermission,HasAddCustomerTypePermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'GET':
            return [HasViewCustomerTypePermission()]
        if self.request.method == 'POST':
            return [HasAddCustomerTypePermission()]
    def get(self, request, *args, **kwargs):
        #inciamos en 0 por defecto
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        customers = Customer_type.objects.all().order_by('id')
        total_customers = customers.count()
        if search_param:
            customers = customers.filter(title__icontains=search_param)
        serializer = self.serializer_class(customers[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_customers,
            "page": page_num,
            "last_page": math.ceil(total_customers/ limit_num),
            "customer_type": serializer.data
        })
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": {"customers": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class Customer_Type_Detail(generics.GenericAPIView):
    queryset = Customer_type.objects.all()
    serializer_class = Customer_typeSerializer
    permission_classes = [IsAuthenticated,HasViewCustomerTypePermission,HasChangeCustomerTypePermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'GET':
            return [HasViewCustomerTypePermission()]
        if self.request.method == 'PATCH':
            return [HasChangeCustomerTypePermission()]
    def get_customer_type(self, pk, *args, **kwargs):
        try:
            return Customer_type.objects.get(pk=pk)
        except:
            return None
    def get(self,request, pk, *args, **kwargs):
        customer_type = self.get_customer_type(pk=pk)
        if customer_type == None:
            return Response({"error": f"Customer_type with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(customer_type)
        return Response({"data": {"customer_type": serializer.data}}, status=status.HTTP_200_OK)
    def patch(self, request, pk):
        customer_type = self.get_customer_type(pk)
        if customer_type == None:
            return Response({"error": "Customer type not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(customer_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": {"customer_type": serializer.data}}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

search = openapi.Parameter('search', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
customer_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'ci_nit': openapi.Schema(type=openapi.TYPE_STRING),
        'phone': openapi.Schema(type=openapi.TYPE_STRING),
        'degree': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

contact_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'ci_nit': openapi.Schema(type=openapi.TYPE_STRING),
        'phone': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

institution_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'nit': openapi.Schema(type=openapi.TYPE_STRING),
        'contacts': openapi.Schema(type=openapi.TYPE_ARRAY, items=contact_schema),
    }
)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customer_type': openapi.Schema(type=openapi.TYPE_INTEGER),
        'customer': customer_schema,
        'institution': institution_schema,
    }
)
class Customer_Api(generics.GenericAPIView):
    serializer_class = CustomersSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated, HasViewCustomerPermission,HasAddCustomerPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'GET':
            return [HasViewCustomerPermission()]
        if self.request.method == 'POST':
            return [HasAddCustomerPermission()]
    @swagger_auto_schema(
    operation_description="Search es opcional para buscar el cliente",
    manual_parameters=[search],
    )
    def get(self, request, *args, **kwargs):
        serializer_class = CustomersSerializer
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        if search_param:
            customers = Customer.objects.all()
            customers = customers.filter(
                Q(contact__name__icontains=search_param) |
                Q(contact__ci_nit__icontains=search_param) |
                Q(institution_name__icontains=search_param) |
                Q(nit__icontains=search_param)
            )
            total_customers = customers.count()
            serializer = serializer_class(customers[start_num:end_num], many=True)
            return Response({
            "status": "success",
            "total": total_customers,
            "page": page_num,
            "last_page": math.ceil(total_customers/ limit_num),
            "customers": serializer.data
            })
        else:
            customers = Customer.objects.all().order_by('id')
            total_customers = customers.count()
            serializer = serializer_class(customers[start_num:end_num], many=True)
            return Response({
            "status": "success",
            "total": total_customers,
            "page": page_num,
            "last_page": math.ceil(total_customers/ limit_num),
            "customers": serializer.data
            })

    @swagger_auto_schema(
    operation_description="Se envia customer o institution segun el tipo de cliente",
    request_body=request_body_schema
    )
    def post(self, request, *args, **kwargs):
        try:
            customer_type_req = request.data["customer_type"]
            customer_type = Customer_type.objects.get(pk=customer_type_req)
        except:
            return Response({"error":"Customer type no válido"},status=status.HTTP_404_NOT_FOUND)
        if customer_type is not None:
            customer_type_id = customer_type.id
            if customer_type.is_institution == True:
                institutions_data = request.data["institution"]
                institution_name =institutions_data.get("name", None)
                nit = institutions_data.get("nit", None)
                contacts = institutions_data.get("contacts")
                if institution_name is None or nit is None:
                    return Response({"error":"los campos no son válidos"}, status=status.HTTP_400_BAD_REQUEST)
                if Customer.objects.filter(nit=nit).exists():
                    return Response({"error":"La institucion ya esta registrada"}, status=status.HTTP_400_BAD_REQUEST)
                customer_institution = Customer.objects.create(institution_name = institution_name, nit=nit, customer_type_id=customer_type_id)
                for contact in contacts:
                    name = contact.get("name", None)
                    ci_nit = contact.get("ci_nit", None)
                    phone = contact.get("phone", None)
                    degree = contact.get("degree", None)
                    nup = contact.get("nup", None)
                    Contact.objects.create(degree=degree, name=name, ci_nit=ci_nit, nup=nup, phone=phone, customer_id=customer_institution.id, is_customer=False)
                return Response({"message": "Institucion registrado con éxito"}, status=status.HTTP_201_CREATED)
            else:
                #cliente
                customers = request.data["customer"]
                degree = customers.get("degree", None)
                name_customer = customers.get("name",None)
                phone = customers.get("phone", None)
                ci_nit = customers.get("ci_nit", None)
                nup = customers.get("nup", None)
                if name_customer is None or ci_nit is None or phone is None:
                    return Response({"error":"los campos no son válidos"}, status=status.HTTP_400_BAD_REQUEST)
                if Contact.objects.filter(ci_nit=ci_nit).exists():
                    return Response({"error": "El cliente ya existe"}, status=status.HTTP_400_BAD_REQUEST)
                customer = Customer.objects.create(customer_type_id=customer_type_id)
                Contact.objects.create(degree=degree, name=name_customer, ci_nit=ci_nit, nup=nup, phone=phone, customer_id=customer.id)
                return Response({"message": "Cliente registrado con exito" }, status=status.HTTP_201_CREATED)
        return Response({"error":"El tipo de cliente no es válido"}, status=status.HTTP_404_NOT_FOUND)



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

institution_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'nit': openapi.Schema(type=openapi.TYPE_STRING),
        'contacts': openapi.Schema(type=openapi.TYPE_ARRAY, items=contact_schema),
    }
)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customer': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'ci_nit': openapi.Schema(type=openapi.TYPE_STRING),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'degree': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        'institution': institution_schema,
    }
)
class Customer_Detail(generics.GenericAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated,HasChangeCustomerPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'PATCH':
            return [HasChangeCustomerPermission()]
        if self.request.method == 'DELETE':
            return [HasDeleteCustomerPermission()]
    def get_customer(self, pk, **kwargs):
        try:
            return Customer.objects.get(pk=pk)
        except:
            return None
    @swagger_auto_schema(
    operation_description="Para editar clientes se envia customer o institution segun el tipo de cliente, en contactos el id es opcional",
    request_body=request_body_schema
    )
    def patch(self, request, pk, **kwargs):
        customer = Customer.objects.get(pk=pk)
        customer_type = Customer_type.objects.get(pk=customer.customer_type_id)
        if customer_type.is_institution == True:
            institutions_data = request.data["institution"]
            institution_name = institutions_data.get("name")
            institution_nit = institutions_data.get("nit")
            contacts = institutions_data.get("contacts")
            institution = Customer.objects.get(pk=pk)
            institution.institution_name = institution_name
            institution.nit = institution_nit
            institution.save()
            contacts_data = Contact.objects.filter(customer_id = pk)
            for contact_data in contacts_data:
                contact_data.is_active = False
                contact_data.save()

            for contact in contacts:
                contact_id = contact.get("id", None)
                name = contact.get("name")
                ci_nit = contact.get("ci_nit", None)
                phone = contact.get("phone")
                degree = contact.get("degree", None)
                nup = contact.get("nup", None)
                if contact_id is None:
                    Contact.objects.create(degree=degree, name=name, ci_nit=ci_nit, phone=phone, customer_id=institution.id, nup=nup, is_customer=False)
                else:
                    contact_data = Contact.objects.get(pk=contact_id)
                    contact_data.name = name
                    contact_data.ci_nit = ci_nit
                    contact_data.phone = phone
                    contact_data.degree = degree
                    contact_data.nup = nup
                    contact_data.is_active = True
                    contact_data.save()
            return Response({"message": "Institución actualizada"}, status=status.HTTP_200_OK)
        else:
            customers = request.data["customer"]
            degree = customers.get("degree", None)
            name = customers.get("name")
            phone = customers.get("phone", None)
            ci_nit = customers.get("ci_nit")
            nup = customers.get("nup", None)
            customer_data = Contact.objects.get(customer_id =customer.id)
            customer_data.name = name
            customer_data.ci_nit = ci_nit
            customer_data.phone = phone
            customer_data.degree = degree
            customer_data.nup = nup
            customer_data.save()
            return Response({"message":"Cliente actualizado"}, status=status.HTTP_200_OK)
    def delete(self, request, pk, **kwargs):
        try:
            customer = Customer.objects.get(pk=pk)
            customer.delete()
        except Customer.DoesNotExist:
            return Response({"error": "El cliente no existe."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Cliente eliminado exitosamente'})
class identify_affiliate(generics.GenericAPIView):
    def get_token_access(self):
        url = f'{settings.MICROSERVICE_API_URL}/auth/login'
        username = settings.MICROSERVICE_API_USERNAME
        password = settings.MICROSERVICE_API_PASSWORD
        response = requests.post(url, data={'username': username, 'password': password})
        if response.status_code == 200:
            token = response.json().get('payload', {}).get('access_token')
            return token
        else:
            response.raise_for_status()
    def get_police(self, id_card):
        token_de_autenticacion = self.get_token_access()
        url_police = f'{settings.MICROSERVICE_API_URL}/affiliate/affiliate'
        params_police = {
            'identity_card_affiliate': id_card,
            'registration_affiliate': '',
            'name_degree': '',
            'full_name_affiliate': '',
            'name_affiliate_state': '',
            'page': 1,
            'per_page': 10,
            'sortDesc[]': False
        }
        headers = {
            'Authorization': f'Bearer {token_de_autenticacion}'
        }
        response = requests.get(url_police, params=params_police, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            payload_data = response_data.get('payload', {}).get('affiliates', {}).get('data', [])
            length = len(payload_data)
            array=[]
            if length >0:
                for item in payload_data:
                    id_card_affiliate=item.get('identity_card_affiliate')
                    if id_card_affiliate == id_card:
                        name=f"{item.get('first_name_affiliate')or ''} {item.get('second_name_affiliate')or ''} {item.get('last_name_affiliate')or ''} {item.get('mothers_last_name_affiliate')or ''}"
                        name=re.sub(' +',' ',name)
                        data = {
                            'id_affiliate':item.get('id_affiliate', 'No disponible'),
                            'ci': item.get('identity_card_affiliate', 'No disponible'),
                            'name': name,
                            'degree': item.get('name_degree')
                        }
                        array.append(data)
                        return({"data":array, "is_police":True})
            return ({'error':'no hay afiliado con ese ci,', "is_police":False})
        else:
            return ({'error': 'Error en la solicitud al microservicio'})
    def get_spouse(self, id_card):
        token_de_autenticacion = self.get_token_access()
        url_spouse = f'{settings.MICROSERVICE_API_URL}/affiliate/spouse'
        params_spouse = {
            'identity_card_spouses': id_card,
            'registration_affiliate': '',
            'name_degree': '',
            'full_name_affiliate': '',
            'name_affiliate_state': '',
            'page': 1,
            'per_page': 10,
            'sortDesc[]': False
        }
        headers = {
            'Authorization': f'Bearer {token_de_autenticacion}'
        }
        response = requests.get(url_spouse, params=params_spouse, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            payload_data = response_data.get('payload', {}).get('spouses', {}).get('data', [])
            length = len(payload_data)
            array=[]
            if length >0:
                for item in payload_data:
                    id_card_affiliate=item.get('identity_card')
                    if id_card_affiliate == id_card:
                        name=f"{item.get('first_name')or ''} {item.get('second_name')or ''} {item.get('last_name')or ''} {item.get('mothers_last_name')or ''}"
                        name=re.sub(' +',' ',name)
                        data = {
                            'affiliate_id':item.get('affiliate_id'),
                            'ci': id_card,
                            'name': name,
                            'degree': item.get('name_degree')
                        }
                        array.append(data)
                        return({"data":array,"is_spouse":True})
            return ({'error':'no hay afiliado con ese ci',"is_spouse":False})
        else:
            return ({'error': 'Error en la solicitud al microservicio'})
    def get(self,request, id_card):

        police_response=self.get_police(id_card)
        spouse_response=self.get_spouse(id_card)
        if police_response["is_police"] is True:
            return Response(police_response["data"])
        else:
            if spouse_response["is_spouse"] is True:
                return Response(spouse_response["data"])
            else:
                return Response({"message":"no existe el afiliado"})
