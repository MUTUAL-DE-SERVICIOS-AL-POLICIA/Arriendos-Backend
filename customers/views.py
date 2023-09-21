from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .serializer import CustomerSerializer, Customer_typeSerializer, CustomersSerializer, InstitutionSerializer
from django.views.decorators.csrf import csrf_exempt
from .models import Customer, Customer_type, Institution
import math
from datetime import datetime
from rest_framework import status, generics
from django.views import View
from rest_framework import filters
from django.db.models import Q
# Create your views here.
class Institutions_ListCreateView(generics.ListCreateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer

class InstitutionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer


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
    serializer_class = CustomerSerializer
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
        customer_request = request.data.get('customer', {})
        institution_name = customer_request.get('institution', '')
        if institution_name:
            institution=Institution.objects.filter(name=institution_name)
            if institution.exists():
                Institution_current=Institution.objects.get(name=institution_name)
                customer_data = {
                    'name': customer_request.get('name'),
                    'last_name': customer_request.get('last_name'),
                    'ci': customer_request.get('ci'),
                    'phone': customer_request.get('phone'),
                    'customer_type': customer_request.get('customer_type'),
                    'grade':customer_request.get('grade'),
                    'institution': Institution_current.id
                }
                CustomerSerialized=CustomerSerializer(data=customer_data)
                if CustomerSerialized.is_valid():
                    CustomerSerialized.save()
                    return Response({"status": "success", "data": {"Customer": customer_data}}, status=status.HTTP_201_CREATED)
                return Response({"status": "fail", "message": CustomerSerialized.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                institution_data = {
                    'name': institution_name,
                }
                InstitutionSerialized = InstitutionSerializer(data=institution_data)
                if InstitutionSerialized.is_valid():
                    InstitutionSerialized.save()
                    Response_data_institution = {
                        "status": "success",
                        "data": {"Institution": institution_data}
                    }
                Institution_current=Institution.objects.get(name=institution_name)
                customer_data = {
                    'name': customer_request.get('name'),
                    'last_name': customer_request.get('last_name'),
                    'ci': customer_request.get('ci'),
                    'phone': customer_request.get('phone'),
                    'customer_type': customer_request.get('customer_type'),
                    'grade':customer_request.get('grade'),
                    'institution': Institution_current.id
                }
                CustomerSerialized=CustomerSerializer(data=customer_data)
                if CustomerSerialized.is_valid():
                    CustomerSerialized.save()
                    Response_data_Customer ={
                        "status": "success",
                        "data": {"Customer": customer_data}
                        }
                    combined_response = [Response_data_institution, Response_data_Customer]
                    return Response(combined_response, status=status.HTTP_201_CREATED)
                return Response({"status": "fail", "message": CustomerSerialized.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            customer_data = {
                    'name': customer_request.get('name'),
                    'last_name': customer_request.get('last_name'),
                    'ci': customer_request.get('ci'),
                    'phone': customer_request.get('phone'),
                    'customer_type': customer_request.get('customer_type'),
                    'grade':customer_request.get('grade'),
                    'institution': customer_request.get('institution')
                }
            CustomerSerialized=CustomerSerializer(data=customer_data)
            if CustomerSerialized.is_valid():
                CustomerSerialized.save()
                return Response({"status": "success", "data": {"Customer": customer_data}}, status=status.HTTP_201_CREATED)
            return Response({"status": "fail", "message": CustomerSerialized.errors}, status=status.HTTP_400_BAD_REQUEST)

class Customer_Detail(generics.GenericAPIView):
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
            return Response({"status": "fail", "message": f"Customer with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(customer)
        return Response({"status": "success", "data": {"customer": serializer.data}}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        customer = self.get_customer(pk=pk)
        if customer == None:
            return Response({"status": "fail", "message": f"Customer with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"customer": serializer.data}}, status=status.HTTP_200_OK)
        return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class InstitutionSearchView(generics.ListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query))
        return queryset