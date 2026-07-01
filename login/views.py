"""
Vistas de autenticación y gestión de usuarios LDAP.

Este módulo contiene:
- get_user_permissions: Función para obtener permisos RBAC de un usuario
- Bind_User_Ldap: Función para autenticar usuario contra LDAP
- Connect_Ldap: Vista para probar conexión LDAP
- Auth: Vista principal de autenticación (login)
- Users_Ldap: Vista para listar usuarios del directorio LDAP

Flujo de autenticación:
1. Si LDAP está habilitado (LDAP_STATUS=True):
   - Intenta autenticar contra LDAP
   - Si LDAP falla, retorna error 401
2. Si LDAP está deshabilitado:
   - Autentica contra la base de datos local
3. Si la autenticación es exitosa:
   - Genera tokens JWT
   - Retorna datos del usuario, rol y permisos RBAC

Autor: Dilan Torrez
Fecha: 2026
"""

from django.conf import settings
from rest_framework.response import Response
from django.http import JsonResponse
from ldap3 import Server, Connection, ALL, SUBTREE
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, generics
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from users.serializers import UserCustomSerializer
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from roles.models import UserRole, RolePermission
from rest_framework.permissions import IsAuthenticated
from roles.permissions import HasModulePermission


def get_user_permissions(user):
    """
    Obtiene los permisos del usuario basado en su rol RBAC.

    Esta función es utilizada por la vista Auth para retornar
    los permisos del usuario en la respuesta de login.

    Parámetros:
        - user: Instancia de User de Django

    Retorna:
        - Tupla (role_name, permissions)
        - role_name: Nombre del rol o None si no tiene rol
        - permissions: Lista de permisos en formato "modulo.permiso"
                      (ej: ["products.view", "leases.add"])

    Ejemplo de uso:
        role_name, permissions = get_user_permissions(user)
        # role_name: "Operador"
        # permissions: ["products.view", "leases.view", "leases.add"]
    """
    try:
        # Buscar el rol asignado al usuario
        user_role = UserRole.objects.get(user=user)
        role = user_role.role

        # Verificar que el rol esté activo
        if not role.is_active:
            return None, []

        # Obtener los permisos del rol por módulo
        role_permissions = RolePermission.objects.filter(role=role).select_related('module')
        permissions = []
        for rp in role_permissions:
            for perm in rp.permissions.all():
                # Formato: "modulo.permiso" (ej: "products.view")
                permissions.append(f"{rp.module.codename}.{perm.codename}")

        return role.name, permissions
    except UserRole.DoesNotExist:
        # Si no tiene rol, retorna permisos vacíos
        return None, []

def Bind_User_Ldap(user, password):
    """
    Autentica un usuario contra el servidor LDAP.

    Realiza la conexión al directorio LDAP y valida las credenciales
    del usuario. Utiliza las credenciales de servicio configuradas
    en settings.py para la conexión inicial.

    Parámetros:
        - user: Nombre de usuario LDAP (uid)
        - password: Contraseña del usuario

    Retorna:
        - True: Si la autenticación fue exitosa
        - None: Si la autenticación falló

    Configuración requerida en settings.py:
        - LDAP_SERVER: Dirección del servidor LDAP
        - LDAP_USER: Usuario de servicio para conexión
        - LDAP_PASSWORD: Contraseña de servicio
        - LDAP_USER_DN: DN base para buscar usuarios
    """
    ldap_server = settings.LDAP_SERVER
    ldap_user = settings.LDAP_USER
    ldap_password = settings.LDAP_PASSWORD
    server = Server(ldap_server, get_info=ALL)
    # Conexión inicial con credenciales de servicio
    connection = Connection(server, ldap_user, ldap_password, auto_bind=True)
    # Construir DN del usuario: uid=usuario,ou=users,dc=...
    user_dn = f"uid={user}, {settings.LDAP_USER_DN}"
    try:
        # Intentar autenticar al usuario con su contraseña
        with Connection(server, user_dn, password, auto_bind=True):
            return True
    except:
        return None


def Connect_Ldap(request):
    """
    Prueba la conexión al servidor LDAP.

    Utilizada para verificar que la configuración LDAP sea correcta
    y el servidor esté accesible.

    Retorna:
        - 202: {"estado": "conectado"} si la conexión fue exitosa
        - 404: {"error": "falló la conexión"} si falló

    URL: /api/login/ldap/connect/
    """
    ldap_server = settings.LDAP_SERVER
    ldap_user = settings.LDAP_USER
    ldap_password = settings.LDAP_PASSWORD
    server = Server(ldap_server, get_info=ALL)
    connection = Connection(server, ldap_user, ldap_password, auto_bind=True)
    try:
        with connection:
            return JsonResponse({"estado":"conectado"}, status=202)
    except:
        return JsonResponse({"error":"falló la conexión"}, status=404)

User = get_user_model()


class Auth(TokenObtainPairView):
    """
    Vista principal de autenticación (login).

    Extiende TokenObtainPairView de DRF SimpleJWT para agregar
    información adicional del usuario y sus permisos RBAC.

    Flujo de autenticación:
    1. Si LDAP está habilitado (LDAP_STATUS=True):
       a. Intenta autenticar contra LDAP
       b. Si LDAP falla, retorna error 401
       c. Si LDAP es exitoso, sincroniza contraseña en BD local
    2. Si LDAP está deshabilitado:
       a. Autentica contra la base de datos local
    3. Si la autenticación es exitosa:
       a. Genera tokens JWT (access y refresh)
       b. Retorna datos del usuario y permisos RBAC

    Estructura de respuesta exitosa (200 OK):
    {
        "access": "token_jwt...",
        "refresh": "token_refresh...",
        "user_id": 1,
        "username": "admin",
        "first_name": "Administrador",
        "last_name": "Sistema",
        "role": "Operador",
        "permissions": ["products.view", "leases.view", ...]
    }

    Estructura de error (401 Unauthorized):
    {
        "error": "Credenciales LDAP inválidas"
    }

    URL: /api/login/auth/
    Método HTTP: POST
    """

    def post(self, request, *args, **kwargs):
        user = request.data.get('username')
        password = request.data.get('password')

        # Si LDAP está habilitado, intentar autenticación LDAP
        if settings.LDAP_STATUS == True:
            if Bind_User_Ldap(user, password):
                # LDAP exitoso: sincronizar contraseña en BD local
                user = User.objects.get(username=user)
                user.password = make_password(password)
                user.save()

                # Generar tokens JWT
                response = super().post(request, *args, **kwargs)
                if response.status_code == status.HTTP_200_OK:
                    user = User.objects.filter(username=request.data['username']).first()
                    response.data['user_id'] = user.id
                    response.data['username'] = user.username
                    response.data['first_name'] = user.first_name
                    response.data['last_name'] = user.last_name

                    # Obtener permisos RBAC del usuario
                    role_name, permissions = get_user_permissions(user)
                    response.data['role'] = role_name
                    response.data['permissions'] = permissions
            else:
                # LDAP falló: retornar error de credenciales
                return Response({'error': 'Credenciales LDAP inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # LDAP deshabilitado: autenticar contra BD local
            response = super().post(request, *args, **kwargs)
            if response.status_code == status.HTTP_200_OK:
                user = User.objects.filter(username=request.data['username']).first()
                response.data['user_id'] = user.id
                response.data['username'] = user.username
                response.data['first_name'] = user.first_name
                response.data['last_name'] = user.last_name

                # Obtener permisos RBAC del usuario
                role_name, permissions = get_user_permissions(user)
                response.data['role'] = role_name
                response.data['permissions'] = permissions

        return response

class Users_Ldap(generics.GenericAPIView):
    """
    Vista para listar usuarios del directorio LDAP que no existen en la BD.

    Consulta el directorio LDAP y retorna los usuarios que:
    1. Existen en el directorio LDAP
    2. NO existen en la base de datos local

    Esto permite identificar qué usuarios LDAP pueden ser importados
    al sistema.

    Permisos requeridos: users.view (Ver usuarios)
    Método HTTP: GET

    Estructura de respuesta (202 Accepted):
    {
        "message": "List of users LDAP",
        "users": [
            {
                "username": "usuario1",
                "first_name": "Nombre",
                "last_name": "Apellido",
                "email": "correo@ejemplo.com"
            },
            ...
        ]
    }

    Configuración LDAP requerida en settings.py:
        - LDAP_SERVER: Dirección del servidor LDAP
        - LDAP_USER: Usuario de servicio
        - LDAP_PASSWORD: Contraseña de servicio
        - LDAP_BASE: Base DN para búsqueda
        - LDAP_FILTER: Filtro de búsqueda
        - ATTRIBUTES: Atributos a retornar

    URL: /api/login/ldap/users/
    """
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'

    @swagger_auto_schema(
        operation_description="Listado de usuarios LDAP",
    )
    def get(self, request, *args, **kwargs):
        serializer_class = UserCustomSerializer
        queryset = User.objects.all()

        # Conectar al servidor LDAP
        ldap_server = settings.LDAP_SERVER
        ldap_password = settings.LDAP_PASSWORD
        server = Server(ldap_server, get_info=ALL)
        connection = Connection(server, settings.LDAP_USER, ldap_password, auto_bind=True)

        # Buscar usuarios en el directorio LDAP
        connection.search(settings.LDAP_BASE, settings.LDAP_FILTER, SUBTREE, attributes=settings.ATTRIBUTES)

        # Obtener usuarios de la BD local para comparar
        data = []
        users_dba = User.objects.all()
        user_to_compare = []
        for user_dba in users_dba:
            user_list = user_dba.username
            user_to_compare.append(user_list)

        # Filtrar usuarios que NO existen en la BD local
        for entry in connection.entries:
            if not entry.uid in user_to_compare:
                user = {
                    "username": f"{entry.uid}",
                    "first_name": f"{entry.givenName}",
                    "last_name": f"{entry.sn}",
                    "email": f"{entry.mail}"
                }
                data.append(user)

        response_data = {"message": "List of users LDAP", "users": data}
        return JsonResponse(response_data, safe=False, status=status.HTTP_202_ACCEPTED)