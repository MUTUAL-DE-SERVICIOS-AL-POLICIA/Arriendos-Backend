from rest_framework import generics, status
from rest_framework.views import APIView
from .models import Rate, HourRange, Product, Price, Price_Additional_Hour
from customers.models import Customer_type
from .serializers import RateSerializer, HourRangeSerializer, ProductsSerializer, ProductSerializer, PriceSerializer, PriceAdditionalHourSerializer
from leases.models import Selected_Product
from rest_framework.response import Response
import math
from requirements.models import RateRequirement
class Rate_Api(generics.GenericAPIView):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()

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
class Rate_Detail(generics.GenericAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

    def get_rate(self, pk, *args, **kwargs):
        try:
            return Rate.objects.get(pk=pk)
        except:
            return None
    def get(self, request, pk, *args, **kwargs):
        rate = self.get_rate(pk=pk)
        if rate == None:
            return Response({"status":"fail", "message": f"Rate with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(rate, data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success", "data": {"rate": serializer.data}}, status=status.HTTP_201_CREATED)
        return Response({"status":"fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Product_Api(generics.GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_product(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except:
            return None
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
class Product_Detail(generics.GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_product(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except:
            return None
    def get(self, request, pk, *args, **kwargs):
        product = self.get_product(pk=pk)
        if product == None:
            return Response({"status": "fail", "message": "Product with id: {pk} not found"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(product)
        return Response({"status": "success", "data": {"product": serializer.data}}, status=status.HTTP_200_OK)
    def patch(self, request, pk):
        product = self.get_product(pk=pk)
        if product == None:
            return Response({"status": "success", "message": f"Product with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"product": serializer.data}}, status=status.HTTP_200_OK)
        return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
class HourRange_List_Create_View(generics.ListCreateAPIView):
    queryset = HourRange.objects.all()
    serializer_class = HourRangeSerializer

class HourRange_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = HourRange.objects.all()
    serializer_class = HourRangeSerializer

class Price_List_Create_View(generics.ListCreateAPIView):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer

class Price_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset=Price.objects.all()
    serializer_class = PriceSerializer
class Additional_Hour_List_Create_View(generics.ListCreateAPIView):
    queryset = Price_Additional_Hour.objects.all()
    serializer_class = PriceAdditionalHourSerializer

class Additional_Hour_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = Price_Additional_Hour.objects.all()
    serializer_class = PriceAdditionalHourSerializer
class Get_price_additional_hour(generics.ListAPIView):
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
            return Response({"no existe el producto seleccionado"}, status=status.HTTP_404_NOT_FOUND)
class Posible_product(APIView):
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