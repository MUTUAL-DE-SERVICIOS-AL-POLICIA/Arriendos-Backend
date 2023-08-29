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
from django.conf import settings
import math

# Create your views here.
class User_Ldap(APIView):
    serializer_class = UserCustomSerializer
    queryset = User.objects.all()
    def get(self, request):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        users = User.objects.all()
        total_users = users.count()
        if search_param:
            users = users.filter(first_name__icontains=search_param)
        serializer = self.serializer_class(users[start_num:end_num], many=True)
        return Response({
            "status": "sname 'Asuccess",
            "total": total_users,
            "page": page_num,
            "last_page": math.ceil(total_users/ limit_num),
            "users": serializer.data
        })
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'El usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'El correo ya existe'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        user.save()
        return Response({"message":"Usuario registrado con exito", "user": user.id, "username": user.username, "email": user.email, "first_name": user.first_name, "last_name": user.last_name}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@csrf_exempt
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

    def get(self, request, *args, **kwargs):
        serializer_class = AssignsSerializer
        queryset = Assign.objects.all()
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        assings = Assign.objects.all()
        total_assings = assings.count()
        if search_param:
            assings = assings.filter(first_name__icontains=search_param)
        serializer = serializer_class(assings[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_assings,
            "page": page_num,
            "last_page": math.ceil(total_assings/ limit_num),
            "assings": serializer.data
            })
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success","data": {"assings": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "data": serializer.errors}, status=status.HTTP_400_BAD)
        
class Assign_Detail(generics.GenericAPIView):
    queryset = Assign.objects.all()
    serializer_class = AssignSerializer

    def get_assing(self, pk, *args, **kwargs):
        try:
            return Assign.objects.get(pk=pk)
        except:
            return None
    
    def get(self, request, pk, *args, **kwargs):
        assing = self.get_assing(pk=pk)
        if assing == None:
            return Response({"status": "fail", "message": f"Assing with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(assing)
        return Response({"status": "success", "data": {"assing": serializer.data}}, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        assing = self.get_assing(pk=pk)
        if assing == None:
            return Response({"status": "fail", "message": f"Assing with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(assing, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"assing": serializer.data}}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "fail", "data": serializer.errors}, status=status.HTTP_400_BAD)
