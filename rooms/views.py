from rest_framework import generics, status
from .models import Property, Room, Sub_Environment
from .serializers import PropertySerializer, RoomSerializer, Sub_EnvironmentSerializer
from django.http import JsonResponse
from rest_framework.response import Response
import math

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
            sub_environments = Sub_Environment.objects.filter(room_id = room.id)
            sub_environment_data = []
            for sub_environment in sub_environments:
                sub_environment_rooms = {
                    'name': sub_environment.name,
                    'state': sub_environment.state,
                    'room': sub_environment.room_id,
                    'quantity': sub_environment.quantity
                }
                sub_environment_data.append(sub_environment_rooms)
            room_data = {
                'id': room.id,
                'name': room.name,
                'capacity': room.capacity,
                'warranty': room.warranty,
                'is_active': room.is_active,
                'group': room.group,
                'sub_environments': sub_environment_data
            }
            property_data['rooms'].append(room_data)

        response_data.append(property_data)
    return JsonResponse({'properties': response_data}, safe=False, json_dumps_params={'ensure_ascii': False})

class Sub_Environment_Api(generics.GenericAPIView):
    queryset = Sub_Environment.objects.all()
    serializer_class = Sub_EnvironmentSerializer

    def get(self, request):
        serializer_class = Sub_EnvironmentSerializer
        page_num = int(request.GET.get('page',0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        sub_environments = Sub_Environment.objects.all()
        total_sub_environments = sub_environments.count()
        serializer = serializer_class(sub_environments[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_sub_environments,
            "page": page_num,
            "last_page": math.ceil(total_sub_environments/ limit_num),
            "assigns": serializer.data
        })

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success", "data":{ "sub_environments": serializer.data }}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status":"fail", "data":serializer.errors}, status=status.HTTP_404_NOT_FOUND)

class Sub_Environment_Detail(generics.GenericAPIView):
    queryset = Sub_Environment.objects.all()
    serializer_class = Sub_EnvironmentSerializer

    def get_sub_environment(self, pk):
        try:
            return Sub_Environment.objects.get(pk=pk)
        except:
            return None
    def get(self, request, pk):
        sub_environment = self.get_sub_environment(pk)
        if sub_environment == None:
            return Response({"status":"fail", "message":"Sub ambiente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(sub_environment)
        return Response({"status":"success", "data":{"sub_environment":serializer.data}}, status=status.HTTP_200_OK)
    def patch(self, request, pk):
        sub_environment = self.get_sub_environment(pk)
        if sub_environment == None:
            return Response({"status":"fail", "message":"Sub ambiente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(sub_environment, data=request.data, partial= True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success", "data":{"sub_environment":serializer.data}}, status=status.HTTP_200_OK)
        return Response({"status":"fail", "message": serializer.errors}, status=status.HTTP_404_NOT_FOUND)