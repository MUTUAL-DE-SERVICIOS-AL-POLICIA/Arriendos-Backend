from rest_framework import generics, status
from .models import Rate, HourRange, Product
from customers.models import Customer_type
from .serializers import RateSerializer, RatesSerializer, HourRangeSerializer, ProductsSerializer, ProductSerializer
from rest_framework.response import Response
import math
class Rate_Api(generics.GenericAPIView):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()

    def get(self, request, *args, **kwargs):
        serializer_class = RatesSerializer
        queryset = Rate.objects.all()
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        rates = Rate.objects.all()
        total_rates = rates.count()
        if search_param:
            rates = rates.filter(title__icontains=search_param)
        serializer = serializer_class(rates[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_rates,
            "page": page_num,
            "last_page": math.ceil(total_rates/ limit_num),
            "rates": serializer.data
        })
    
    def post(self, request, *args, **kwargs):
        serializer =self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success", "data": {"rate": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status":"fail", "message": serializer.errors}, status=status.HTTP_404_NOT_FOUND)
        
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

    def get(self, request, *args, **kwargs):
        serializer_class = ProductsSerializer
        queryset = Product.objects.all()
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        products = Product.objects.all().order_by('id')
        total_products = products.count()
        if search_param:
            products = Product.filter(title_icotains=search_param)
        serializer = serializer_class(products[start_num:end_num],many=True)
        return Response({
            "status": "success",
            "total": total_products,
            "page": page_num,
            "last_page": math.ceil(total_products/ limit_num),
            "products": serializer.data
        })
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {serializer.data}}, status=status.HTTP_201_CREATED)
        else:
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
