from django.shortcuts import render
from django.conf import settings
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPException
# Create your views her
def connect_ldap(request):
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