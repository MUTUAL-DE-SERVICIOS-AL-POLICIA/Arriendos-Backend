from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .serializer import CustomerSerializer, Customer_typeSerializer, CustomersSerializer, ContactSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import Customer, Customer_type, Contact
import math
from datetime import datetime
from rest_framework import status, generics
from rest_framework import filters
from django.db.models import Q
# Create your views here.

class Customer_Type_Api(generics.GenericAPIView):
    serializer_class = Customer_typeSerializer
    queryset = Customer_type.objects.all()

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
            return Response({"status": "success", "data": {"customers": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class Customer_Type_Detail(generics.GenericAPIView):
    queryset = Customer_type.objects.all()
    serializer_class = Customer_typeSerializer


    def get_customer_type(self, pk, *args, **kwargs):
        try:
            return Customer_type.objects.get(pk=pk)
        except:
            return None
    def get(self,request, pk, *args, **kwargs):
        customer_type = self.get_customer_type(pk=pk)
        if customer_type == None:
            return Response({"status": "fail", "message": f"Customer_type with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(customer_type)
        return Response({"status": "success", "data": {"customer_type": serializer.data}}, status=status.HTTP_200_OK)
    def patch(self, request, pk):
        customer_type = self.get_customer_type(pk)
        if customer_type == None:
            return Response({"status": "fail", "message": "Customer type not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(customer_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"customer_type": serializer.data}}, status=status.HTTP_200_OK)
        return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class Customer_Api(generics.GenericAPIView):
    serializer_class = CustomersSerializer
    queryset = Customer.objects.all()
    def get(self, request, *args, **kwargs):
        serializer_class = CustomersSerializer
        queryset = Customer.objects.all()
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        customers = Customer.objects.all().order_by('id')
        total_customers = customers.count()
        if search_param:
            customers = customers.filter(title__icontains=search_param)
        serializer = serializer_class(customers[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_customers,
            "page": page_num,
            "last_page": math.ceil(total_customers/ limit_num),
            "customers": serializer.data
        })
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
                    return Response({"status": "success", "message":"La institucion ya esta registrada"}, status=status.HTTP_200_OK)
                customer_institution = Customer.objects.create(institution_name = institution_name, nit=nit, customer_type_id=customer_type_id)
                for contact in contacts:
                    name = contact.get("name", None)
                    ci_nit = contact.get("ci_nit", None)
                    phone = contact.get("phone", None)
                    degree = contact.get("degree", None)
                    Contact.objects.create(degree=degree, name=name, ci_nit=ci_nit, phone=phone, customer_id=customer_institution.id, is_customer=False)
                return Response({"message": "Institucion registrado con éxito"}, status=status.HTTP_201_CREATED)
            else:
                #cliente
                customers = request.data["customer"]
                degree = customers.get("degree", None)
                name_customer = customers.get("name",None)
                phone = customers.get("phone", None)
                ci_nit = customers.get("ci_nit", None)
                if name_customer is None or ci_nit is None or phone is None:
                    return Response({"error":"los campos no son válidos"}, status=status.HTTP_400_BAD_REQUEST)
                if Contact.objects.filter(ci_nit=ci_nit).exists():
                    return Response({"message": "El cliente ya existe"}, status=status.HTTP_200_OK)
                customer = Customer.objects.create(customer_type_id=customer_type_id)
                Contact.objects.create(degree=degree, name=name_customer, ci_nit=ci_nit, phone=phone, customer_id=customer.id)
                return Response({"message": "Cliente registrado con exito" }, status=status.HTTP_201_CREATED)
        return HttpResponse({"error":"El tipo de cliente no es válido"}, status=status.HTTP_404_NOT_FOUND)

class Customer_Detail(generics.GenericAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    def get_customer(self, pk, **kwargs):
        try:
            return Customer.objects.get(pk=pk)
        except:
            return None
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
                if contact_id is None:
                    Contact.objects.create(degree=degree, name=name, ci_nit=ci_nit, phone=phone, customer_id=institution.id, is_customer=False)
                else:
                    contact_data = Contact.objects.get(pk=contact_id)
                    contact_data.name = name
                    contact_data.ci_nit = ci_nit
                    contact_data.phone = phone
                    contact_data.degree = degree
                    contact_data.is_active = True
                    contact_data.save()
            return Response({"message": "Institución actualizada"}, status=status.HTTP_200_OK)
        else:
            customers = request.data["customer"]
            degree = customers.get("degree", None)
            name = customers.get("name")
            phone = customers.get("phone", None)
            ci_nit = customers.get("ci_nit")
            customer_data = Contact.objects.get(customer_id =customer.id)
            customer_data.name = name
            customer_data.ci_nit = ci_nit
            customer_data.phone = phone
            customer_data.degree = degree
            customer_data.save()
            return Response({"message":"Cliente actualizado"}, status=status.HTTP_200_OK)

class CustomerInsitution_Detail(generics.GenericAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_customer(self, pk, *args, **kwargs):
        try:
            return Customer.objects.get(pk=pk)
        except:
            return None
    def get(self, request, pk, *args, **kwargs):
        customer = self.get_customer(pk=pk)
        if customer == None:
            return Response({"status": "fail", "message": f"Customer institution with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(customer)
        return Response({"status": "success", "data": {"customer institution": serializer.data}}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        customer = self.get_customer(pk=pk)
        if customer == None:
            return Response({"status": "fail", "message": f"Customer institution with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"customer institution": serializer.data}}, status=status.HTTP_200_OK)
        return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class Contact_Api(generics.GenericAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        degree = request.data.get('degree', None)
        ci_nit = request.data.get('ci_nit', None)
        phone = request.data.get('phone')
        is_customer = False
        customer = request.data.get('customer')
        customers = Customer.objects.get(pk=customer)
        if customers:
            if customers.institution_name == None:
                return Response({"status": "fail", "message": "No se puede agregar el contacto"}, status=status.HTTP_404_NOT_FOUND)
        if Contact.objects.filter(ci_nit=ci_nit, customer_id =customer).exists():
            return Response({"status": "Fail", "message":"El contacto ya existe"}, status=status.HTTP_404_NOT_FOUND)
        try:
            contact = Contact.objects.create(name=name, phone=phone, is_customer=is_customer, ci_nit=ci_nit, degree=degree, customer_id=customer)
            return Response({"status": "success", "message":"Contacto registrado con éxito"}, status=status.HTTP_201_CREATED)
        except:
            return Response({"status":"fail"}, status=status.HTTP_400_BAD_REQUEST)
class Contact_Detail(generics.GenericAPIView):
    queryset= Contact.objects.all()
    serializer_class=ContactSerializer

    def get_contact(self, pk):
        try:
            return Contact.objects.get(pk=pk)
        except:
            return None
    def get(self, pk, request):
        contact = self.get_contact(pk=pk)
        if contact == None:
            return Response({"status": "fail", "message": f"Contact with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(contact)
        return Response({"status": "success", "data": {"contact": serializer.data}}, status=status.HTTP_200_OK)
    def patch(self, request, pk, *args, **kwargs):
        contact = self.get_contact(pk=pk)
        if contact == None:
            return Response({"status": "fail", "message": f"Contact with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"contact": serializer.data}}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": serializer.errors}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk): 
        if not Contact.objects.filter(pk=pk).exists():
            return Response({"status":"fail"}, status=status.HTTP_404_NOT_FOUND)
        contact = Contact.objects.get(pk=pk)
        if contact.is_active == True:
            contact.is_active= False
            contact.save()
            return Response({"status": "success", "message":"Contacto desactivado"}, status=status.HTTP_200_OK)
        else:
            contact.is_active= True
            contact.save()
            return Response({"status":"success", "message":"Contacto activado"}, status=status.HTTP_200_OK)
        