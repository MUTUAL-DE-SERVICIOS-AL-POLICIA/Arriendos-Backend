from django.shortcuts import render
from django.conf import settings
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPException
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

#from django.core import serializers
import json

def Bind_User_Ldap(user, password):
    ldap_server = settings.LDAP_SERVER 
    ldap_user = settings.LDAP_USER
    ldap_password = settings.LDAP_PASSWORD
    server = Server(ldap_server, get_info=ALL)
    connection = Connection(server, ldap_user, ldap_password, auto_bind=True)  
    user_dn = f"uid={user}, {settings.LDAP_USER_DN}"
    try:
        with Connection(server, user_dn, password, auto_bind=True):
            return True
    except:
        return None

def Connect_Ldap(request):
    ldap_server = settings.LDAP_SERVER 
    ldap_user = settings.LDAP_USER
    ldap_password = settings.LDAP_PASSWORD
    server = Server(ldap_server, get_info=ALL)
    connection = Connection(server, ldap_user, ldap_password, auto_bind=True)
    try:
        with connection:
            return JsonResponse({"estado":"conectado"}, status=202)
    except:
        return JsonResponse({"estado":"falló la conexión"}, status=404)
@csrf_exempt
@api_view(['POST'])
def Search_User_Ldap(request):
    user=request.data.get('user')
    password=request.data.get('password')
    if Bind_User_Ldap(user, password)==True: 
        return HttpResponse("usuario válido")
    else:
        return HttpResponse("no coincide el usuario y contraseña")

User = get_user_model()
class Auth(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        user=request.data.get('username')
        password=request.data.get('password')
        if(settings.LDAP_STATUS==True):
            if Bind_User_Ldap(user, password):
                response = super().post(request, *args, **kwargs)
                if response.status_code == status.HTTP_200_OK:
                    user = User.objects.filter(username=request.data['username']).first()
                    response.data['user_id'] = user.id
                    response.data['username'] = user.username
                    response.data['first_name'] = user.first_name
                    response.data['last_name'] = user.last_name
                    if not user or not user.check_password(request.data['password']):
                        response.data['detail'] = "Credenciales inválidas"
                        response.status_code = status.HTTP_401_UNAUTHORIZED
            else:
                 return Response({'detail': 'Credenciales LDAP inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            response = super().post(request, *args, **kwargs)
            if response.status_code == status.HTTP_200_OK:
                user = User.objects.filter(username=request.data['username']).first()
                response.data['user_id'] = user.id
                response.data['username'] = user.username
                response.data['user_id'] = user.id
                response.data['first_name'] = user.first_name
                response.data['last_name'] = user.last_name
                if not user or not user.check_password(request.data['password']):
                    response.data['detail'] = "Credenciales inválidas"
                    response.status_code = status.HTTP_401_UNAUTHORIZED
        return response

def Users_ldap(request):
    ldap_server = settings.LDAP_SERVER
    ldap_password = settings.LDAP_PASSWORD
    server = Server(ldap_server, get_info=ALL)
    connection = Connection(server, settings.LDAP_USER, ldap_password, auto_bind=True) 
    connection.search(settings.LDAP_BASE, settings.LDAP_FILTER, SUBTREE, attributes=settings.ATTRIBUTES)
    data = []
    for entry in connection.entries:
        user = [{'first_name': entry.givenName, 'last_name': entry.sn, 'email': entry.mail, 'username': entry.uid }]
        data.append(user)
    return HttpResponse(data, status=200)