from django.shortcuts import render
from django.conf import settings
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPException
# Create your views here
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

        

