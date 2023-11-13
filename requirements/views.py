from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from .models import RateRequirement, Requirement,Requirement_Delivered
from .serializer import RateRequirementSerializer, RequirementSerializer, RateWithRelatedDataSerializer
from products.models import Rate
from customers.models import Customer_type
from django.db import models
import math
from datetime import datetime
from leases.models import Rental, Selected_Product
from Arriendos_Backend.util import required_fields
from .function import Make_Rental_Form
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .permissions import *
from rest_framework.permissions import IsAuthenticated

class Requirement_Api(generics.GenericAPIView):
    serializer_class = RequirementSerializer
    queryset = Requirement.objects.all()
    permission_classes = [IsAuthenticated, HasViewRequirementPermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewRequirementPermission()]
        if self.request.method == 'POST':
            return [HasAddRequirementPermission()]
    @swagger_auto_schema(
    operation_description="Lista de requisitos",
    )
    def get(self, request, *args, **kw):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        requirements = Requirement.objects.filter(is_active = True).order_by('id')
        total_requirements = requirements.count()
        serializer = self.serializer_class(requirements[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_requirements,
            "page": page_num,
            "last_page": math.ceil(total_requirements/ limit_num),
           'requirements': serializer.data,
        })
    @swagger_auto_schema(
    operation_description="Crear requisitos",
    )
    def post(self, request, *args, **kw):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": {"requirement": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class Requirement_Detail(generics.GenericAPIView):
    queryset = Requirement.objects.all()
    serializer_class = RequirementSerializer
    permission_classes = [IsAuthenticated, HasChangeRequirementPermission, HasDeleteRequirementPermission]
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [HasChangeRequirementPermission()]
        if self.request.method == 'DELETE':
            return [HasDeleteRequirementPermission()]
    def get_requirement(self, pk, *args, **kw):
        try:
            return Requirement.objects.get(pk=pk)
        except:
            return None

    def patch(self, request, pk, *args, **kw):
        requirement = self.get_requirement(pk)
        if requirement == None:
            return Response({"error": "El requisito no existe"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(requirement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": {"requirement": serializer.data}}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not Requirement.objects.filter(pk=pk).exists():
            return Response({"error":"El requisito no existe"}, status=status.HTTP_404_NOT_FOUND)
        requirement = Requirement.objects.get(pk=pk)
        if requirement.is_active == True:
            requirement.is_active= False
            requirement.save()
            return Response({"message":"Requisito desactivado"}, status=status.HTTP_200_OK)
        else:
            requirement.is_active= True
            requirement.save()
            return Response({"message":"Requisito activado"}, status=status.HTTP_200_OK)
class RateWithRelatedDataView(generics.ListAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateWithRelatedDataSerializer
    permission_classes = [IsAuthenticated, HasViewRateRequirementPermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewRateRequirementPermission()]
    def get(self, request):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit',10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        rates = Rate.objects.all().order_by('id')
        total_rates = rates.count()
        serializer = self.serializer_class(rates[start_num:end_num], many=True)
        return Response({
            "status":"success",
            "total": total_rates,
            "page": page_num,
            "last_page": math.ceil(total_rates/ limit_num),
            "rates": serializer.data
        })

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'rate': openapi.Schema(type=openapi.TYPE_STRING),
        'requirement': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_INTEGER)
        ),
        'customer_type': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_INTEGER)
        ),
    }
)

class RateRequirement_Api(generics.GenericAPIView):
    serializer_class = RateRequirementSerializer
    queryset = RateRequirement.objects.all()
    permission_classes = [IsAuthenticated, HasViewRateRequirementPermission, HasAddRateRequirementPermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewRateRequirementPermission()]
        if self.request.method == 'POST':
            return [HasAddRateRequirementPermission()]
    def get(self, request, *args, **kwargs):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit',10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        raterequirements = RateRequirement.objects.all()
        total_raterequirements = raterequirements.count()
        if search_param:
            raterequirements = raterequirements.filter(requirement_icontains=search_param)
        serializer = self.serializer_class(raterequirements[start_num:end_num], many=True)
        return Response ({
            "status": "success",
            "total": total_raterequirements,
            "page": page_num,
            "last_page": math.ceil(total_raterequirements/ limit_num),
            "raterequirements": serializer.data
        })

    @swagger_auto_schema(
    operation_description="Crear tarifa con tipo de cliente y requisitos",
    request_body=request_body_schema
    )

    def post(self, request, *args, **kwargs):
        rate=request.data.get("rate")
        customer_types = request.data.get("customer_type")
        requirements = request.data.get("requirement")
        if rate is None or customer_types is None or requirements is None:
            return Response({"error": "Los datos enviados no son los correctos"}, status=status.HTTP_400_BAD_REQUEST)
        if Rate.objects.filter(name = rate).exists():
            return Response({"error": "La tarifa ya existe"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            rate = Rate.objects.create(name = rate)
        rate=Rate.objects.get(pk=rate.id)
        for customer_type in customer_types:
            customer_type = Customer_type.objects.get(pk=customer_type)
            for requirement in requirements:
                if Requirement.objects.filter(pk=requirement).exists():
                    requirement = Requirement.objects.get(pk=requirement)
                    RateRequirement.objects.create(requirement = requirement, rate = rate, customer_type = customer_type)
        return Response({"message":"Tarifa creada con éxito"}, status=status.HTTP_201_CREATED)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'requirement': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_INTEGER)
        ),
        'customer_type': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_INTEGER)
        ),
    }
)

class RateRequirement_Detail(generics.GenericAPIView):
    queryset = RateRequirement.objects.all()
    serializer_class = RateRequirementSerializer
    permission_classes = [IsAuthenticated, HasViewRateRequirementPermission, HasChangeRateRequirementPermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewRateRequirementPermission()]
        if self.request.method == 'PATCH':
            return [HasChangeRateRequirementPermission()]
    def get_raterequirement(self, pk, *args, **kw):
        try:
            return RateRequirement.objects.get(pk=pk)
        except:
            return None

    def get(self, request, pk, *args, **kw):
        raterequirement = self.get_raterequirement(pk=pk)
        if raterequirement == None:
            return Response({"error": "No existe el requisito asignado a la tarifa"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(raterequirement)
        return Response({"data": {"raterequirement": serializer.data}}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
    operation_description="Editar tarifa con tipo de cliente y requisitos",
    request_body=request_body_schema
    )

    def patch(self, request, pk, *args, **kw):
        name=request.data.get("name")
        customer_types = request.data.get("customer_type")
        rate_requirements = request.data.get("requirement")
        rates_group = RateRequirement.objects.filter(rate=pk)
        if name is not None:
            rate_name=Rate.objects.get(pk=pk)
            rate_name.name= name
            rate_name.save()
        
        for rate_group in rates_group:
            rate_group.is_active = False
            rate_group.save()
        for customer_type in customer_types:
            customer = RateRequirement.objects.filter(customer_type_id=customer_type, rate_id= pk).exists()
            if customer:
                for rate_requirement in rate_requirements:
                    requirement = RateRequirement.objects.filter(requirement_id=rate_requirement, customer_type_id = customer_type, rate_id=pk).exists()
                    if requirement:
                        requirement = RateRequirement.objects.get(requirement_id=rate_requirement, customer_type_id = customer_type, rate_id=pk)
                        requirement.is_active = True
                        requirement.save()
                    else:
                        try:
                            requirement = RateRequirement.objects.create(requirement_id=rate_requirement, customer_type_id=customer_type, rate_id=pk)
                        except:
                            return Response({"error":"No se pudo agregar el cliente y tarifa"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                for rate_requirement in rate_requirements:
                    new_customer = RateRequirement.objects.create(requirement_id=rate_requirement, customer_type_id=customer_type, rate_id=pk)
        return Response({"message":"Tarifa actualizada con éxito"}, status=status.HTTP_200_OK)

class Requirements_customer(generics.GenericAPIView):
     @swagger_auto_schema(
     operation_description="Requisitos requeridos y opcionales",
     )
     def get(self, request):
        rental_id = request.GET.get('rental', None)
        try:
            selected_product = Selected_Product.objects.filter(rental_id=rental_id).first()
            rate_id = selected_product.product.rate.id
            required_requirements = RateRequirement.objects.filter(rate_id=rate_id)
            required_requirements_list =  []
            for required_requirement in required_requirements:
                required_requirement_data ={
                    "id":required_requirement.requirement.id,
                    "name":required_requirement.requirement.requirement_name,
                    "is_active":required_requirement.requirement.is_active
                }
                required_requirements_list.append(required_requirement_data)
            all_requirements = Requirement.objects.all()
            required_requirement_ids = [req['id'] for req in required_requirements_list]
            other_requirements = all_requirements.exclude(id__in=required_requirement_ids)
            other_requirements_list = []
            for requirement in other_requirements:
                other_requirement_data = {
                    "id":requirement.id,
                    "name": requirement.requirement_name,
                    "is_active": requirement.is_active
                }
                other_requirements_list.append(other_requirement_data)
            return Response({"data": {"required_requirements": required_requirements_list,"optional_requirements":other_requirements_list}}, status=status.HTTP_200_OK)
        except Rental.DoesNotExist:
            return Response({"error": "No se encontró el arriendo"}, status=status.HTTP_404_NOT_FOUND)
class Register_delivered_requirement(generics.ListAPIView):
        def post(self, request):
            validated_fields = ["rental"]
            error_message = required_fields(request, validated_fields)
            if error_message:
                return Response(error_message, status=400)
            rental_id = request.data["rental"]
            list_requirements = request.data.get("list_requirements")
            try:
                if list_requirements:
                    rental = Rental.objects.get(pk=rental_id)
                    for requirement in list_requirements:
                        requirements_delivered = Requirement_Delivered.objects.filter(requirement_id = requirement, rental_id = rental_id).exists()
                        if requirements_delivered:
                            return Response({"error": "Los requisitos ya existen"}, status=status.HTTP_404_NOT_FOUND)
                    for requirement in list_requirements:
                        requirement_delivered = Requirement_Delivered()
                        requirement_register=Requirement.objects.get(pk=requirement)
                        requirement_delivered.rental = rental
                        requirement_delivered.requirement = requirement_register
                        requirement_delivered.save()

                    now = datetime.now()
                    year = now.year
                    max_contract_number = Rental.objects.filter(created_at__year=year).aggregate(models.Max('contract_number'))['contract_number__max']
                    if max_contract_number is None:
                        max_contract_number = 0
                    else:
                        max_contract_number = int(max_contract_number.split('-')[0])
                    contract_number = '{}-{}'.format(max_contract_number +1, year)
                    rental.contract_number = contract_number
                    rental.save()
                    return Make_Rental_Form(request, rental_id)
                else:
                    return Make_Rental_Form(request, rental_id)
            except Rental.DoesNotExist:
                    return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)