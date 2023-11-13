from rest_framework import generics, status
from rest_framework.views import APIView
from .models import Rate, HourRange, Product, Price, Price_Additional_Hour
from customers.models import Customer_type
from .serializers import RateSerializer, HourRangeSerializer, ProductsSerializer, ProductSerializer, PriceSerializer, PriceAdditionalHourSerializer
from leases.models import Selected_Product
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import math
from requirements.models import RateRequirement
from .permissions import *
from rest_framework.permissions import IsAuthenticated

class Rate_Api(generics.GenericAPIView):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()
    permission_classes = [IsAuthenticated, HasViewRatePermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewRatePermission()]
    @swagger_auto_schema(
    operation_description="Lista de Tarifas",
    )
    def get(self, request, *args, **kwargs):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        rates = Rate.objects.all()
        total_rates = rates.count()
        if search_param:
            rates = rates.filter(title__icontains=search_param)
        serializer = self.serializer_class(rates[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_rates,
            "page": page_num,
            "last_page": math.ceil(total_rates/ limit_num),
            "rates": serializer.data
        })

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'day': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING)
        ),
        'rate':openapi.Schema(type=openapi.TYPE_INTEGER),
        'room':openapi.Schema(type=openapi.TYPE_INTEGER),
        'hour_range': openapi.Schema(type=openapi.TYPE_INTEGER),
        'mount': openapi.Schema(type=openapi.TYPE_INTEGER)
    }
)
class Product_Api(generics.GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, HasViewProductPermission, HasAddroductPermission, HasChangeProductPermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewProductPermission()]
        if self.request.method == 'POST':
            return [HasAddroductPermission()]
        if self.request.method == 'PATCH':
            return [HasChangeProductPermission()]
    def get_product(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except:
            return None
    @swagger_auto_schema(
    operation_description="Lista de productos y precio",
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ProductsSerializer(queryset, many=True)
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 1))
        start_num = page_num * limit_num
        end_num = limit_num * (page_num + 1)
        total_products = queryset.count()
        products_with_active_prices = []
        for product in queryset:
            active_price_data = ProductSerializer.get_active_price(product)
            queryset_list = list(queryset)
            product_data = serializer.data[queryset_list.index(product)]
            if active_price_data:
                product_data['mount'] = active_price_data.get("mount")
            products_with_active_prices.append(product_data)
        paged_products = products_with_active_prices[start_num:end_num]

        return Response({
        "status": "success",
        "total": total_products,
        "page": page_num,
        "last_page": math.ceil(total_products/ limit_num),
        "products": paged_products
        })
    @swagger_auto_schema(
    operation_description="Crear productos",
    request_body=request_body_schema
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            Product_saved=serializer.save()
            mount=request.data.get('mount', '')
            price_data = {
                "mount": mount,
                "is_active": True,
                "product": Product_saved.id
            }
            PriceSerialized=PriceSerializer(data=price_data)
            if (PriceSerialized.is_valid()):
                PriceSerialized.save()
                combined_response=[serializer.data, PriceSerialized.data]
                return Response({"status": "success", "data": combined_response}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": "fail", "message": PriceSerialized.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    @swagger_auto_schema(
    operation_description="Actualizar producto y precio",
    request_body=request_body_schema
    )
    def patch(self,request, pk ):
        product = self.get_product(pk=pk)
        if product == None:
            return Response({"status": "success", "message": f"Product with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        if 'mount' in request.data:
            mount_value = request.data['mount']
            Price.objects.filter(product_id=pk).update(is_active=False)
            new_price={
                "mount":mount_value,
                "is_active":True,
                "product":pk
            }
            price_serialized=PriceSerializer(data=new_price)
            if price_serialized.is_valid():
                price_serialized.save()
                price_response=price_serialized.data
            product_serialized = ProductSerializer(product, data=request.data, partial=True)
            if product_serialized.is_valid():
                product_serialized.save()
                product_response=product_serialized.data
                combined_response = {
                    'price': price_response,
                    'product': product_response
                }
                return Response({"status": "success", "data": combined_response}, status=status.HTTP_200_OK)
            return Response({"status": "fail", "message": product_serialized.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.serializer_class(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": {"product": serializer.data}}, status=status.HTTP_200_OK)
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class HourRange_List_Create_View(generics.ListCreateAPIView):
    queryset = HourRange.objects.all()
    serializer_class = HourRangeSerializer
    permission_classes = [IsAuthenticated, HasAddHourRangePermission, HasViewHourRangePermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewHourRangePermission()]
        if self.request.method == 'POST':
            return [HasAddHourRangePermission()]

class HourRange_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = HourRange.objects.all()
    serializer_class = HourRangeSerializer
    permission_classes = [IsAuthenticated, HasChangeHourRangePermission, HasDeleteHourRangePermission]
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [HasChangeHourRangePermission()]
        if self.request.method == 'DELETE':
            return [HasDeleteHourRangePermission()]

class Price_List_Create_View(generics.ListCreateAPIView):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [IsAuthenticated, HasAddPricePermission, HasViewPricePermission]
    def get_permissions(self):
        if self.request.method == 'POST':
            return [HasAddPricePermission()]
        if self.request.method == 'GET':
            return [HasViewPricePermission()]

class Price_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset=Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [IsAuthenticated, HasChangePricePermission, HasDeletePricePermission]
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [HasChangePricePermission()]
        if self.request.method == 'DELETE':
            return [HasDeletePricePermission()]
class Additional_Hour_List_Create_View(generics.ListCreateAPIView):
    queryset = Price_Additional_Hour.objects.all()
    serializer_class = PriceAdditionalHourSerializer
    permission_classes = [IsAuthenticated, HasAddAdditionalHourPermission, HasViewAdditionalHourPermission]
    def get_permissions(self):
        if self.request.method == 'POST':
            return [HasAddAdditionalHourPermission()]
        if self.request.method == 'GET':
            return [HasViewAdditionalHourPermission()]

class Additional_Hour_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = Price_Additional_Hour.objects.all()
    serializer_class = PriceAdditionalHourSerializer
    permission_classes = [IsAuthenticated, HasChangeAdditionalHourPermission, HasDeleteAdditionalHourPermission]
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [HasChangeAdditionalHourPermission()]
        if self.request.method == 'DELETE':
            return [HasDeleteAdditionalHourPermission()]

selected_product = openapi.Parameter('selected_product', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)

class Get_price_additional_hour(generics.ListAPIView):
    permission_classes = [IsAuthenticated, HasViewAdditionalHourPermission]
    def get_permissions(self):
        print(self.request.user.get_all_permissions())
        if self.request.method == 'GET':
            return [HasViewAdditionalHourPermission()]
    @swagger_auto_schema(
    operation_description="Precio de hora adicional del producto seleccionado",
    manual_parameters=[selected_product],
    )
    def get(self,request):
        selected_product_id = request.query_params.get('selected_product')
        try:
            selected_product=Selected_Product.objects.get(pk=selected_product_id)
            room = selected_product.product.room.id
            hour = selected_product.product.hour_range.id
            price_additional_hour=Price_Additional_Hour.objects.filter(room=room, hourRange=hour, state=True)
            if price_additional_hour.exists():
                price=price_additional_hour.first().mount
                return Response({"price":price}, status=status.HTTP_200_OK)
            return Response({"error": "No existe hora extra para ese producto"}, status=status.HTTP_404_NOT_FOUND)
        except Selected_Product.DoesNotExist:
            return Response({"error": "No existe el producto seleccionado"}, status=status.HTTP_404_NOT_FOUND)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customer_type': openapi.Schema(type=openapi.TYPE_INTEGER),
        'room_id': openapi.Schema(type=openapi.TYPE_INTEGER)
    }
)
class Posible_product(APIView):
    permission_classes = [IsAuthenticated, HasViewProductPermission]
    def get_permissions(self):
        if self.request.method == 'POST':
            return [HasViewProductPermission()]
    @swagger_auto_schema(
    request_body=request_body_schema,
    )
    def post(self, request):
        customer_type_id = request.data.get('customer_type')
        room_id=request.data.get('room_id')
        try:
            rate_requirement = RateRequirement.objects.filter(customer_type_id=customer_type_id).first()
            if rate_requirement:
                rate_id = rate_requirement.rate.id
                products_with_rate = Product.objects.filter(rate=rate_id,room=room_id)
                serializer = ProductsSerializer(products_with_rate, many=True)
                products_with_active_prices=[]
                for product in products_with_rate:
                    active_price_data = ProductSerializer.get_active_price(product)
                    product_list = list(products_with_rate)
                    product_data = serializer.data[product_list.index(product)]
                    if active_price_data:
                        product_data['mount'] = active_price_data.get("mount")
                        products_with_active_prices.append(product_data)
                return Response({'status': 'success', 'products': products_with_active_prices})
            else:
                customer=Customer_type.objects.get(pk=customer_type_id)
                return Response({"error": f"No hay requisitos asociados a la tarifa perteneciente al tipo de cliente: {customer.name}"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer_type.DoesNotExist:
            return Response({"error": "Tipo de cliente no encontrado"}, status=status.HTTP_400_BAD_REQUEST)