from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserCustomSerializer
from .serializers import AssignSerializer, AssignsSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPException
from django.contrib.auth.models import User
from .models import Assign
from rest_framework import status, generics
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
import math

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
    }
)
# Create your views here.
class User_Ldap(APIView):
    serializer_class = UserCustomSerializer
    queryset = User.objects.all()
    @swagger_auto_schema(
    operation_description="Listado de usuarios",
    )
    def get(self, request):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        users = User.objects.all().order_by('id')
        total_users = users.count()
        if search_param:
            users = users.filter(first_name__icontains=search_param)
        serializer = self.serializer_class(users[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_users,
            "page": page_num,
            "last_page": math.ceil(total_users/ limit_num),
            "users": serializer.data
        })
    @swagger_auto_schema(
    operation_description="Crear usuarios con LDAP",
    request_body=request_body_schema
    )
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        user=request.data.get('username')
        ldap_server = settings.LDAP_SERVER
        ldap_user = settings.LDAP_USER
        ldap_password = settings.LDAP_PASSWORD
        server = Server(ldap_server, get_info=ALL)
        connection = Connection(server, ldap_user, ldap_password, auto_bind=True)
        search_base = settings.LDAP_BASE
        search_filter = f"(uid={user})"
        search_attributes = settings.ATTRIBUTES
        connection.search(search_base, search_filter, SUBTREE, attributes=search_attributes)
        for entry in connection.entries:
            if (first_name == entry.givenName and last_name == entry.sn and username == entry.uid and email == entry.mail):
                if User.objects.filter(username=username).exists():
                    return Response({'error': 'El usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)
                if User.objects.filter(email=email).exists():
                    return Response({'error': 'El correo ya existe'}, status=status.HTTP_400_BAD_REQUEST)
                user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name)
                return Response({"message":"Usuario registrado con exito", "user": user.id, "username": user.username, "email": user.email, "first_name": user.first_name, "last_name": user.last_name}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": "fail"}, status=status.HTTP_404_NOT_FOUND)
            
class User_Delete(generics.GenericAPIView):
    @swagger_auto_schema(
    operation_description="Desactivar usuarios",
    )
    def delete(self, request, pk):
        if not User.objects.filter(pk=pk).exists():
            return Response({"status":"fail"}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(pk=pk)
        if user.is_active == True:
            user.is_active= False
            user.save()
            return Response({"message":"Usuario desactivado"}, status=status.HTTP_200_OK)
        else:
            user.is_active= True
            user.save()
            return Response({"message":"Usuario activado"}, status=status.HTTP_200_OK)


request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'user': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

@csrf_exempt
@swagger_auto_schema(
    method='post',
    operation_description="API para obtener datos del usuario",
    request_body=request_body_schema
    )
@api_view(['POST'])
def get_user(request):
    user=request.data.get('user')
    ldap_server = settings.LDAP_SERVER
    ldap_user = settings.LDAP_USER
    ldap_password = settings.LDAP_PASSWORD
    server = Server(ldap_server, get_info=ALL)
    connection = Connection(server, ldap_user, ldap_password, auto_bind=True)
    search_base = settings.LDAP_BASE
    search_filter = f"(uid={user})"
    search_attributes = settings.ATTRIBUTES
    connection.search(search_base, search_filter, SUBTREE, attributes=search_attributes)
    data = []
    for entry in connection.entries:
        user = [{'first_name': entry.givenName, 'last_name': entry.sn, 'email': entry.mail, 'username': entry.uid }]
        data.append(user)
    return HttpResponse(data, status=200)

class Assign_Api(generics.GenericAPIView):
    serializer_class = AssignSerializer
    queryset = Assign.objects.all()
    @swagger_auto_schema(
    operation_description="Usuarios y ambientes asignados",
    )
    def get(self, request, *args, **kwargs):
        serializer_class = AssignsSerializer
        queryset = Assign.objects.all()
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        assigns = Assign.objects.all()
        total_assigns = assigns.count()
        if search_param:
            assigns = assigns.filter(user__icontains=search_param)
        serializer = serializer_class(assigns[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_assigns,
            "page": page_num,
            "last_page": math.ceil(total_assigns/ limit_num),
            "assigns": serializer.data
            })
    @swagger_auto_schema(
    operation_description="Asignación de usuarios y ambientes",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": {"assigns": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD)

class Assign_Detail(generics.GenericAPIView):
    queryset = Assign.objects.all()
    serializer_class = AssignSerializer

    def get_assign(self, pk, *args, **kwargs):
        try:
            return Assign.objects.get(pk=pk)
        except:
            return None

    def get(self, request, pk, *args, **kwargs):
        assign = self.get_assign(pk=pk)
        if assign == None:
            return Response({"error": f"Assign with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(assign)
        return Response({"data": {"assign": serializer.data}}, status=status.HTTP_200_OK)
    @swagger_auto_schema(
    operation_description="Editar asignación de ambientes a usuarios",
    )
    def patch(self, request, pk):
        assign = self.get_assign(pk=pk)
        if assign == None:
            return Response({"error": f"Assign with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(assign, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": {"assign": serializer.data}}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD)