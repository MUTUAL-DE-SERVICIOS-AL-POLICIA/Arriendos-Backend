from rest_framework import generics
from .models import Rate, Time, Product
from .serializers import RateSerializer, TimeSerializer, ProductSerializer

class Rate_List_Create_View(generics.ListCreateAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

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
