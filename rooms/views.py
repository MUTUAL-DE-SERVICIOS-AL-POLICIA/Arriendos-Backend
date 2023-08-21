from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import Property, Room
from .serializers import PropertySerializer, RoomSerializer
from django.http import JsonResponse

class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class PropertyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class RoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
def List_Rooms_Properties(request, id_number):
    rooms = Room.objects.filter(property=id_number)
    response_data = [{'name': room.name, 'capacity': room.capacity, 'warranty': room.warranty, 'is_active': room.is_active} for room in rooms]
    return JsonResponse({"rooms": response_data}, safe=False, json_dumps_params={'ensure_ascii': False})