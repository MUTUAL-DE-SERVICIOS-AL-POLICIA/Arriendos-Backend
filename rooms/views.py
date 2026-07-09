from rest_framework import generics, status
from .models import Property, Room, Sub_Room
from .serializers import PropertySerializer, RoomSerializer, Sub_RoomSerializer
from rest_framework.response import Response
import math
from roles.permissions import HasModulePermission
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from threadlocals.threadlocals import set_thread_variable
from django.db.models import Prefetch
class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'rooms'
    def get(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        return super().get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        return super().post(request, *args, **kwargs)

class PropertyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'rooms'
    def patch(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        return super().patch(request, *args, **kwargs)
    def delete(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        return super().delete(request, *args, **kwargs)
class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'rooms'
    def get(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        return super().get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        return super().post(request, *args, **kwargs)

class RoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'rooms'
    def patch(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        return super().patch(request, *args, **kwargs)
    def delete(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        return super().delete(request, *args, **kwargs)
class List_Properties_with_Rooms(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'rooms'
    @swagger_auto_schema(
    operation_description="Listado de ambientes y propiedades",
    )
    def get(self, request):
        set_thread_variable('thread_user', request.user)
        properties = Property.objects.prefetch_related(
            Prefetch('room_set', queryset=Room.objects.prefetch_related(
                Prefetch('sub_room_set', queryset=Sub_Room.objects.all())
            ))
        ).all()
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
            rooms = property.room_set.all()
            for room in rooms:
                sub_rooms = room.sub_room_set.all()
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
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'rooms'
    @swagger_auto_schema(
    operation_description="Lista de sub ambientes",
    )
    def get(self, request):
        set_thread_variable('thread_user', request.user)
        serializer_class = Sub_RoomSerializer
        page_num = int(request.GET.get('page',0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        sub_rooms = Sub_Room.objects.all()
        total_sub_rooms = sub_rooms.count()
        if limit_num == -1:
            paginated = sub_rooms
        else:
            start_num = (page_num) * limit_num
            end_num = limit_num * (page_num + 1)
            paginated = sub_rooms[start_num:end_num]
        serializer = serializer_class(paginated, many=True)
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
        set_thread_variable('thread_user', request.user)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":{ "sub_rooms": serializer.data }}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error":serializer.errors}, status=status.HTTP_404_NOT_FOUND)

class Sub_Room_Detail(generics.GenericAPIView):
    queryset = Sub_Room.objects.all()
    serializer_class = Sub_RoomSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'rooms'
    def get_sub_room(self, pk):
        try:
            return Sub_Room.objects.get(pk=pk)
        except Sub_Room.DoesNotExist:
            return None
    def get(self, request, pk):
        set_thread_variable('thread_user', request.user)
        sub_room = self.get_sub_room(pk)
        if sub_room == None:
            return Response({"error":"Sub ambiente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(sub_room)
        return Response({"data":{"sub_room":serializer.data}}, status=status.HTTP_200_OK)
    @swagger_auto_schema(
    operation_description="Actualizar sub ambiente",
    )
    def patch(self, request, pk):
        set_thread_variable('thread_user', request.user)
        sub_room = self.get_sub_room(pk)
        if sub_room == None:
            return Response({"error":"Sub ambiente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(sub_room, data=request.data, partial= True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":{"sub_room":serializer.data}}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_404_NOT_FOUND)
