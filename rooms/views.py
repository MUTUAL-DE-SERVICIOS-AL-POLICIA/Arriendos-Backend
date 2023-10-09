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
def List_Properties_with_Rooms(request):
    properties = Property.objects.all()
    response_data = []

    for property in properties:
        property_data = {
            'id': property.id,
            'name': property.name,
            'photo': request.build_absolute_uri(property.photo.url),  # Agrega la URL de la foto si la necesitas
            'rooms': []
        }
        rooms = Room.objects.filter(property=property)
        for room in rooms:
            room_data = {
                'id': room.id,
                'name': room.name,
                'capacity': room.capacity,
                'warranty': room.warranty,
                'is_active': room.is_active,
                'group': room.group
            }
            property_data['rooms'].append(room_data)

        response_data.append(property_data)

    return JsonResponse({'properties': response_data}, safe=False, json_dumps_params={'ensure_ascii': False})