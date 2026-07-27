from rest_framework.views import APIView
from .serializers import UserCustomSerializer
from .serializers import AssignSerializer, AssignsSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.decorators import api_view
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPException
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Assign
from rest_framework import status, generics
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from threadlocals.threadlocals import set_thread_variable
from rest_framework.permissions import IsAuthenticated
from roles.permissions import HasModulePermission
from roles.models import UserRole
from .audit import create_rbac_audit
import math
import re
import logging

logger = logging.getLogger('business')

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
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'
    @swagger_auto_schema(
    operation_description="Listado de usuarios",
    )
    def get(self, request):
        set_thread_variable('thread_user', request.user)
        try:
            page_num = int(request.GET.get('page', 0))
            limit_num = int(request.GET.get('limit', 10))
        except (ValueError, TypeError):
            return Response({"error": "Parámetros 'page' y 'limit' deben ser numéricos"}, status=status.HTTP_400_BAD_REQUEST)
        search_param = request.GET.get('search')
        users = User.objects.prefetch_related(
            'user_role', 'user_role__role'
        ).order_by('id')
        if search_param:
            users = users.filter(first_name__icontains=search_param)
        total_users = users.count()
        if limit_num == -1:
            paginated = users
        else:
            start_num = page_num * limit_num
            end_num = limit_num * (page_num + 1)
            paginated = users[start_num:end_num]
        serializer = self.serializer_class(paginated, many=True)
        return Response({
            "status": "success",
            "total": total_users,
            "page": page_num,
            "last_page": math.ceil(total_users/ limit_num) if limit_num > 0 else 0,
            "users": serializer.data
        })
    @swagger_auto_schema(
    operation_description="Crear usuarios con LDAP",
    request_body=request_body_schema
    )
    def post(self, request):
        set_thread_variable('thread_user', request.user)
        username = request.data.get('username')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        user=request.data.get('username')
        ldap_server = settings.LDAP_SERVER
        ldap_user = settings.LDAP_USER
        ldap_password = settings.LDAP_PASSWORD
        server = Server(ldap_server, get_info=ALL)
        connection = None
        try:
            connection = Connection(server, ldap_user, ldap_password, auto_bind=True)
            search_base = settings.LDAP_BASE
            safe_user = re.escape(str(user)) if user else ''
            search_filter = f"(uid={safe_user})"
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
            return Response({"error": "Usuario no encontrado en LDAP"}, status=status.HTTP_404_NOT_FOUND)
        except LDAPException as e:
            logger.error(f"LDAP_ERROR: {str(e)}")
            return Response({"error": "Error de conexión con LDAP"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        finally:
            if connection:
                try:
                    connection.unbind()
                except Exception:
                    pass
class User_Delete(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'
    @swagger_auto_schema(
    operation_description="Desactivar usuarios",
    )
    def delete(self, request, pk):
        set_thread_variable('thread_user', request.user)
        if not User.objects.filter(pk=pk).exists():
            return Response({"status":"fail", "message":"Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(pk=pk)

        # No permitir que un usuario se desactive a si mismo
        if user.pk == request.user.pk:
            return Response({
                "status": "fail",
                "message": "No puedes desactivar tu propia cuenta"
            }, status=status.HTTP_400_BAD_REQUEST)

        # No permitir desactivar usuario is_superuser
        if user.is_superuser:
            return Response({
                "status": "fail",
                "message": "No se puede desactivar al usuario administrador del sistema"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Operador no puede desactivar/activar Administradores
        if not request.user.is_superuser:
            try:
                request_user_role = UserRole.objects.get(user=request.user)
                if request_user_role.role.name == 'Operador':
                    try:
                        target_role = UserRole.objects.get(user=user)
                        if target_role.role.name == 'Administrador':
                            return Response({"status": "fail", "message": "No puedes desactivar a un administrador"}, status=status.HTTP_403_FORBIDDEN)
                    except UserRole.DoesNotExist:
                        pass
            except UserRole.DoesNotExist:
                pass

        # No permitir desactivar al ultimo administrador
        try:
            target_role = UserRole.objects.get(user=user)
            if target_role.role.name == 'Administrador':
                admin_count = UserRole.objects.filter(role__name='Administrador').count()
                if admin_count <= 1:
                    return Response({
                        "status": "fail",
                        "message": "No se puede desactivar al último administrador"
                    }, status=status.HTTP_400_BAD_REQUEST)
        except UserRole.DoesNotExist:
            pass

        if user.is_active == True:
            user.is_active= False
            user.save()
            create_rbac_audit(request.user, "USER_DEACTIVATE", f"Desactivó usuario '{user.username}'", user.id)
            return Response({"status":"success", "message":"Usuario desactivado"}, status=status.HTTP_200_OK)
        else:
            user.is_active= True
            user.save()
            create_rbac_audit(request.user, "USER_ACTIVATE", f"Activó usuario '{user.username}'", user.id)
            return Response({"status":"success", "message":"Usuario activado"}, status=status.HTTP_200_OK)


request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'user': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

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
    connection = None
    try:
        connection = Connection(server, ldap_user, ldap_password, auto_bind=True)
        search_base = settings.LDAP_BASE
        safe_user = re.escape(str(user)) if user else ''
        search_filter = f"(uid={safe_user})"
        search_attributes = settings.ATTRIBUTES
        connection.search(search_base, search_filter, SUBTREE, attributes=search_attributes)
        data = []
        for entry in connection.entries:
            user_data = {'first_name': str(entry.givenName) if entry.givenName else '', 'last_name': str(entry.sn) if entry.sn else '', 'email': str(entry.mail) if entry.mail else '', 'username': str(entry.uid) if entry.uid else ''}
            data.append(user_data)
        return Response(data, status=200)
    except LDAPException as e:
        return Response({"error": f"Error de conexión LDAP: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    finally:
        if connection:
            try:
                connection.unbind()
            except Exception:
                pass

class Assign_Api(generics.GenericAPIView):
    serializer_class = AssignSerializer
    queryset = Assign.objects.all()
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'
    @swagger_auto_schema(
    operation_description="Usuarios y ambientes asignados",
    )
    def get(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        serializer_class = AssignsSerializer
        queryset = Assign.objects.all()
        try:
            page_num = int(request.GET.get('page', 0))
            limit_num = int(request.GET.get('limit', 10))
        except (ValueError, TypeError):
            return Response({"error": "Parámetros 'page' y 'limit' deben ser numéricos"}, status=status.HTTP_400_BAD_REQUEST)
        search_param = request.GET.get('search')
        assigns = Assign.objects.select_related('user', 'room', 'room__property').prefetch_related(
            'user__user_role', 'user__user_role__role'
        )
        total_assigns = assigns.count()
        if search_param:
            assigns = assigns.filter(user__username__icontains=search_param)
        if limit_num == -1:
            paginated = assigns
        else:
            start_num = page_num * limit_num
            end_num = limit_num * (page_num + 1)
            paginated = assigns[start_num:end_num]
        serializer = serializer_class(paginated, many=True)
        return Response({
            "status": "success",
            "total": total_assigns,
            "page": page_num,
            "last_page": math.ceil(total_assigns/ limit_num) if limit_num > 0 else 0,
            "assigns": serializer.data
            })
    @swagger_auto_schema(
    operation_description="Asignación de usuarios y ambientes",
    )
    def post(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        serializer = self.serializer_class(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": {"assigns": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class Assign_Detail(generics.GenericAPIView):
    queryset = Assign.objects.all()
    serializer_class = AssignSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'

    def get_assign(self, pk, *args, **kwargs):
        try:
            return Assign.objects.get(pk=pk)
        except Assign.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        assign = self.get_assign(pk=pk)
        if assign == None:
            return Response({"error": f"Assign with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(assign)
        return Response({"data": {"assign": serializer.data}}, status=status.HTTP_200_OK)
    @swagger_auto_schema(
    operation_description="Editar asignación de ambientes a usuarios",
    )
    def patch(self, request, pk):
        set_thread_variable('thread_user', request.user)
        assign = self.get_assign(pk=pk)
        if assign == None:
            return Response({"error": f"Assign with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(assign, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": {"assign": serializer.data}}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
