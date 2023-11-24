from rest_framework import generics, status
from .models import Property, Room, Sub_Room
from .serializers import PropertySerializer, RoomSerializer, Sub_RoomSerializer
from rest_framework.response import Response
import math
from .permissions import *
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from threadlocals.threadlocals import set_thread_variable
class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, HasAddPropertyPermission, HasViewPropertyPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'POST':
            return [IsAuthenticated(), HasAddPropertyPermission()]
        elif self.request.method == 'GET':
            return [IsAuthenticated(), HasViewPropertyPermission()]
        return super().get_permissions()

class PropertyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, HasChangePropertyPermission, HasDeletePropertyPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), HasChangePropertyPermission()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), HasDeletePropertyPermission()]
        return super().get_permissions()
class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, HasAddRoomPermission, HasViewRoomPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'POST':
            return [IsAuthenticated(), HasAddRoomPermission()]
        elif self.request.method == 'GET':
            return [IsAuthenticated(), HasViewRoomPermission()]
        return super().get_permissions()

class RoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, HasChangeRoomPermission, HasDeleteRoomPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), HasChangeRoomPermission()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), HasDeleteRoomPermission()]
        return super().get_permissions()
class List_Properties_with_Rooms(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HasViewPropertyPermission, HasViewRoomPermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewPropertyPermission(), HasViewRoomPermission()]
    @swagger_auto_schema(
    operation_description="Listado de ambientes y propiedades",
    )
    def get(self, request):
        properties = Property.objects.all()
        response_data = []
        for property in properties:
            property_data = {
                'id': property.id,
                'name': property.name,
                'address': property.address,
                'department': property.department,
                'photo': request.build_absolute_uri(property.photo.url),
                'rooms': []
            }
            rooms = Room.objects.filter(property=property)
            for room in rooms:
                sub_rooms = Sub_Room.objects.filter(room_id = room.id)
                sub_room_data = []
                for sub_room in sub_rooms:
                    sub_room_rooms = {
                        'name': sub_room.name,
                        'state': sub_room.state,
                        'room': sub_room.room_id,
                        'quantity': sub_room.quantity
                    }
                    sub_room_data.append(sub_room_rooms)
                room_data = {
                    'id': room.id,
                    'name': room.name,
                    'capacity': room.capacity,
                    'warranty': room.warranty,
                    'is_active': room.is_active,
                    'group': room.group,
                    'sub_rooms': sub_room_data
                }
                property_data['rooms'].append(room_data)
            response_data.append(property_data)
        return Response({'properties': response_data},status=status.HTTP_200_OK )
class Sub_Room_Api(generics.GenericAPIView):
    queryset = Sub_Room.objects.all()
    serializer_class = Sub_RoomSerializer
    permission_classes = [IsAuthenticated, HasViewSub_RoomPermission, HasAddSub_RoomPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'GET':
            return [HasViewSub_RoomPermission()]
        if self.request.method == 'POST':
            return [HasAddSub_RoomPermission()]
    @swagger_auto_schema(
    operation_description="Lista de sub ambientes",
    )
    def get(self, request):
        serializer_class = Sub_RoomSerializer
        page_num = int(request.GET.get('page',0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        sub_rooms = Sub_Room.objects.all()
        total_sub_rooms = sub_rooms.count()
        serializer = serializer_class(sub_rooms[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_sub_rooms,
            "page": page_num,
            "last_page": math.ceil(total_sub_rooms/ limit_num),
            "sub_rooms": serializer.data
        })
    @swagger_auto_schema(
    operation_description="Crear sub ambiente",
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":{ "sub_rooms": serializer.data }}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error":serializer.errors}, status=status.HTTP_404_NOT_FOUND)

class Sub_Room_Detail(generics.GenericAPIView):
    queryset = Sub_Room.objects.all()
    serializer_class = Sub_RoomSerializer
    permission_classes = [IsAuthenticated, HasChangeSub_RoomPermission, HasViewSub_RoomPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'GET':
            return [HasViewSub_RoomPermission()]
        if self.request.method == 'PATCH':
            return [HasChangeSub_RoomPermission()]
    def get_sub_room(self, pk):
        try:
            return Sub_Room.objects.get(pk=pk)
        except:
            return None
    def get(self, request, pk):
        sub_room = self.get_sub_room(pk)
        if sub_room == None:
            return Response({"error":"Sub ambiente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(sub_room)
        return Response({"data":{"sub_room":serializer.data}}, status=status.HTTP_200_OK)
    @swagger_auto_schema(
    operation_description="Actualizar sub ambiente",
    )
    def patch(self, request, pk):
        sub_room = self.get_sub_room(pk)
        if sub_room == None:
            return Response({"error":"Sub ambiente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(sub_room, data=request.data, partial= True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":{"sub_room":serializer.data}}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_404_NOT_FOUND)