from rest_framework import generics
from .models import Rate, Time, Product
from .serializers import RateSerializer, TimeSerializer, ProductSerializer
from rest_framework.response import Response
import math
class Rate_List_Create_View(generics.ListCreateAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    def get(self, request, *args, **kwargs):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        rates = Rate.objects.all()
        total_customers = rates.count()
        if search_param:
            rates = rates.filter(title__icontains=search_param)
        serializer = self.serializer_class(rates[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_customers,
            "page": page_num,
            "last_page": math.ceil(total_customers/ limit_num),
            "rates": serializer.data
        })

class Rate_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

class Time_List_Create_View(generics.ListCreateAPIView):
    queryset = Time.objects.all()
    serializer_class = TimeSerializer

class Time_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = Time.objects.all()
    serializer_class = TimeSerializer


class Product_List_Create_View(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class Product_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
