"""
Vistas API para el sistema RBAC (Role-Based Access Control).

Este modulo contiene las vistas para gestionar:
- Módulos del sistema (Module)
- Permisos disponibles (Permission)
- Roles y sus permisos (Role, RolePermission)
- Asignación de roles a usuarios (UserRole)
- Consulta de permisos del usuario actual (MyPermissions)

Todas las vistas utilizan HasModulePermission para validar
que el usuario tenga los permisos necesarios sobre el módulo 'users'.

Autor: Dilan Torrez
Fecha: 2026
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Module, Permission, Role, RolePermission, UserRole
from .serializers import (
    ModuleSerializer, PermissionSerializer,
    RoleSerializer, RoleCreateSerializer,
    UserRoleSerializer, UserRoleCreateSerializer,
    UserWithRoleSerializer
)
from roles.permissions import HasModulePermission
from users.audit import create_rbac_audit
import math


class Module_List_View(generics.ListAPIView):
    """
    Vista para listar módulos activos del sistema.

    Retorna la lista de módulos que están habilitados (is_active=True).
    Utilizada al crear/editar roles para mostrar los módulos disponibles.

    Permisos requeridos: users.view (Ver usuarios)
    Método HTTP: GET
    """
    queryset = Module.objects.filter(is_active=True)
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'

    def get(self, request, *args, **kwargs):
        modules = self.get_queryset()
        serializer = self.serializer_class(modules, many=True)
        return Response({
            "status": "success",
            "modules": serializer.data
        })


class Permission_List_View(generics.ListAPIView):
    """
    Vista para listar permisos disponibles del sistema.

    Retorna todos los permisos (Ver, Crear, Editar, Eliminar).
    Utilizada al crear/editar roles para mostrar los permisos disponibles.

    Permisos requeridos: users.view (Ver usuarios)
    Método HTTP: GET
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'

    def get(self, request, *args, **kwargs):
        permissions = self.get_queryset()
        serializer = self.serializer_class(permissions, many=True)
        return Response({
            "status": "success",
            "permissions": serializer.data
        })


class Role_List_Create_View(generics.GenericAPIView):
    """
    Vista para listar y crear roles.

    GET: Retorna lista paginada de roles con búsqueda por nombre.
    POST: Crea un nuevo rol con sus permisos asociados.

    Permisos requeridos:
    - GET: users.view (Ver usuarios)
    - POST: users.add (Crear usuarios)

    Parámetros de consulta (GET):
    - page: Número de página (default: 0)
    - limit: Cantidad de elementos por página (default: total)
    - search: Texto de búsqueda para filtrar por nombre

    Estructura de respuesta GET:
    {
        "status": "success",
        "total": 10,
        "page": 0,
        "last_page": 2,
        "roles": [...]
    }

    Estructura de body POST:
    {
        "name": "Nombre del Rol",
        "description": "Descripción",
        "is_active": true,
        "permissions_data": [
            {"module": 1, "permissions": [1, 2, 3]},
            ...
        ]
    }
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'

    def get(self, request, *args, **kwargs):
        try:
            page_num = int(request.GET.get('page', 0))
            limit_num = int(request.GET.get('limit', 10))
        except (ValueError, TypeError):
            return Response({"error": "Parámetros 'page' y 'limit' deben ser numéricos"}, status=status.HTTP_400_BAD_REQUEST)
        search_param = request.GET.get('search', '')

        roles = Role.objects.prefetch_related('role_permissions__permissions', 'userrole_set')
        if search_param:
            roles = roles.filter(name__icontains=search_param)

        total = roles.count()
        if limit_num == -1:
            paginated = roles
        else:
            start_num = page_num * limit_num
            end_num = limit_num * (page_num + 1)
            paginated = roles[start_num:end_num]
        serializer = RoleSerializer(paginated, many=True)

        return Response({
            "status": "success",
            "total": total,
            "page": page_num,
            "last_page": math.ceil(total / limit_num) if limit_num > 0 else 0,
            "roles": serializer.data
        })

    def post(self, request, *args, **kwargs):
        # Solo Administrador o is_superuser puede crear roles
        if not request.user.is_superuser:
            try:
                user_role = UserRole.objects.get(user=request.user)
                if user_role.role.name != 'Administrador':
                    return Response({"status": "fail", "message": "Solo administradores pueden crear roles"}, status=status.HTTP_403_FORBIDDEN)
            except UserRole.DoesNotExist:
                return Response({"status": "fail", "message": "No tienes un rol asignado"}, status=status.HTTP_403_FORBIDDEN)

        serializer = RoleCreateSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            create_rbac_audit(request.user, "ROLE_CREATE", f"Creó rol '{role.name}'", role.id)
            return Response({
                "status": "success",
                "data": RoleSerializer(role).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "fail",
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class Role_Detail_View(generics.GenericAPIView):
    """
    Vista para obtener, actualizar o eliminar un rol específico.

    GET: Retorna los detalles de un rol con sus permisos.
    PATCH: Actualiza un rol (nombre, descripción, estado, permisos).
    DELETE: Elimina un rol (solo si no tiene usuarios asignados).

    Permisos requeridos:
    - GET: users.view (Ver usuarios)
    - PATCH: users.change (Editar usuarios)
    - DELETE: users.delete (Eliminar usuarios)

    Nota: No se puede eliminar un rol que tenga usuarios asignados.
    Se debe primero desasignar el rol de los usuarios.

    URL: /api/roles/<int:pk>/
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'

    def get(self, request, pk, *args, **kwargs):
        """Obtiene los detalles de un rol por su ID."""
        try:
            role = Role.objects.get(pk=pk)
            serializer = RoleSerializer(role)
            return Response({
                "status": "success",
                "data": serializer.data
            })
        except Role.DoesNotExist:
            return Response({
                "status": "fail",
                "message": "Rol no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk, *args, **kwargs):
        """Actualiza un rol existente (actualización parcial)."""
        # Solo Administrador o is_superuser puede editar roles
        if not request.user.is_superuser:
            try:
                user_role = UserRole.objects.get(user=request.user)
                if user_role.role.name != 'Administrador':
                    return Response({"status": "fail", "message": "Solo administradores pueden editar roles"}, status=status.HTTP_403_FORBIDDEN)
            except UserRole.DoesNotExist:
                return Response({"status": "fail", "message": "No tienes un rol asignado"}, status=status.HTTP_403_FORBIDDEN)

        try:
            role = Role.objects.get(pk=pk)
            serializer = RoleCreateSerializer(role, data=request.data, partial=True)
            if serializer.is_valid():
                role = serializer.save()
                create_rbac_audit(request.user, "ROLE_UPDATE", f"Actualizó rol '{role.name}'", role.id)
                return Response({
                    "status": "success",
                    "data": RoleSerializer(role).data
                })
            return Response({
                "status": "fail",
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Role.DoesNotExist:
            return Response({
                "status": "fail",
                "message": "Rol no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, *args, **kwargs):
        """
        Elimina un rol.
        Valida que no tenga usuarios asignados antes de eliminar.
        Solo Administrador o is_superuser puede eliminar roles.
        """
        # Solo Administrador o is_superuser puede eliminar roles
        if not request.user.is_superuser:
            try:
                user_role = UserRole.objects.get(user=request.user)
                if user_role.role.name != 'Administrador':
                    return Response({"status": "fail", "message": "Solo administradores pueden eliminar roles"}, status=status.HTTP_403_FORBIDDEN)
            except UserRole.DoesNotExist:
                return Response({"status": "fail", "message": "No tienes un rol asignado"}, status=status.HTTP_403_FORBIDDEN)

        try:
            role = Role.objects.get(pk=pk)
            # Verificar si hay usuarios con este rol
            if UserRole.objects.filter(role=role).exists():
                return Response({
                    "status": "fail",
                    "message": "No se puede eliminar un rol asignado a usuarios"
                }, status=status.HTTP_400_BAD_REQUEST)
            role_name = role.name
            role.delete()
            create_rbac_audit(request.user, "ROLE_DELETE", f"Eliminó rol '{role_name}'", pk)
            return Response({
                "status": "success",
                "message": "Rol eliminado correctamente"
            })
        except Role.DoesNotExist:
            return Response({
                "status": "fail",
                "message": "Rol no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)


class UserRole_Assign_View(generics.GenericAPIView):
    """
    Vista para asignar un rol a un usuario.

    POST: Asigna un rol a un usuario. Si el usuario ya tiene un rol,
    lo reemplaza con el nuevo.

    Permisos requeridos: users.change (Editar usuarios)

    Estructura de body:
    {
        "user_id": 1,
        "role_id": 2
    }

    Nota: Un usuario no puede asignarse un rol a sí mismo (validación en serializer).

    URL: /api/roles/assign/
    """
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'

    def post(self, request, *args, **kwargs):
        # Solo Administrador o is_superuser puede asignar roles
        if not request.user.is_superuser:
            try:
                user_role = UserRole.objects.get(user=request.user)
                if user_role.role.name != 'Administrador':
                    return Response({"status": "fail", "message": "Solo administradores pueden asignar roles"}, status=status.HTTP_403_FORBIDDEN)
            except UserRole.DoesNotExist:
                return Response({"status": "fail", "message": "No tienes un rol asignado"}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserRoleCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user_role = serializer.save()
            target_user = User.objects.get(id=user_role.user_id)
            create_rbac_audit(
                request.user, "ROLE_ASSIGN",
                f"Asignó rol '{user_role.role.name}' a usuario '{target_user.username}'",
                user_role.id
            )
            return Response({
                "status": "success",
                "data": UserRoleSerializer(user_role).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "fail",
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserRole_List_View(generics.GenericAPIView):
    """
    Vista para listar todas las asignaciones de roles a usuarios.

    Retorna la lista de todos los usuarios con su rol asignado.
    Utilizada para gestionar las asignaciones de roles.

    Permisos requeridos: users.view (Ver usuarios)
    Método HTTP: GET

    URL: /api/roles/assignments/
    """
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'

    def get(self, request, *args, **kwargs):
        user_roles = UserRole.objects.select_related('user', 'role').all()
        serializer = UserRoleSerializer(user_roles, many=True)
        return Response({
            "status": "success",
            "user_roles": serializer.data
        })


class UserRole_Detail_View(generics.GenericAPIView):
    """
    Vista para eliminar la asignación de rol de un usuario.

    DELETE: Elimina la asignación de rol de un usuario específico.
    Esto deja al usuario sin rol (sin permisos RBAC).

    Permisos requeridos: users.delete (Eliminar usuarios)

    URL: /api/roles/assignments/<int:pk>/
    """
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'users'

    def delete(self, request, pk, *args, **kwargs):
        """Elimina la asignación de rol de un usuario."""
        # Solo Administrador o is_superuser puede quitar roles
        if not request.user.is_superuser:
            try:
                user_role_request = UserRole.objects.get(user=request.user)
                if user_role_request.role.name != 'Administrador':
                    return Response({"status": "fail", "message": "Solo administradores pueden quitar roles"}, status=status.HTTP_403_FORBIDDEN)
            except UserRole.DoesNotExist:
                return Response({"status": "fail", "message": "No tienes un rol asignado"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_role = UserRole.objects.get(pk=pk)
            # No permitir remover último Administrador
            if user_role.role.name == 'Administrador':
                admin_count = UserRole.objects.filter(role__name='Administrador').count()
                if admin_count <= 1:
                    return Response({"status": "fail", "message": "No se puede remover el rol al último administrador"}, status=status.HTTP_400_BAD_REQUEST)

            target_user = User.objects.get(id=user_role.user_id)
            role_name = user_role.role.name
            user_role.delete()
            create_rbac_audit(
                request.user, "ROLE_REMOVE",
                f"Removió rol '{role_name}' de usuario '{target_user.username}'",
                pk
            )
            return Response({
                "status": "success",
                "message": "Rol removido del usuario"
            })
        except UserRole.DoesNotExist:
            return Response({
                "status": "fail",
                "message": "Asignacion no encontrada"
            }, status=status.HTTP_404_NOT_FOUND)


class MyPermissions_View(generics.GenericAPIView):
    """
    Vista para obtener los permisos del usuario autenticado.

    Retorna el rol y la lista de permisos del usuario actual.
    Utilizada por el frontend para saber qué módulos y acciones
    puede realizar el usuario.

    Permisos requeridos: users.view (Ver usuarios)
    Método HTTP: GET

    Estructura de respuesta:
    {
        "status": "success",
        "role": "Operador",
        "permissions": [
            "products.view",
            "leases.view",
            "leases.add",
            ...
        ]
    }

    Si el usuario no tiene rol:
    {
        "status": "success",
        "role": null,
        "permissions": []
    }

    URL: /api/roles/my-permissions/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Obtiene los permisos del usuario autenticado."""
        user = request.user
        try:
            # Obtener el rol del usuario
            user_role = UserRole.objects.get(user=user)
            role = user_role.role

            # Obtener todos los permisos del rol por módulo
            role_permissions = RolePermission.objects.filter(role=role).select_related('module')
            permissions = []
            for rp in role_permissions:
                for perm in rp.permissions.all():
                    # Formato: "modulo.permiso" (ej: "products.view")
                    permissions.append(f"{rp.module.codename}.{perm.codename}")

            return Response({
                "status": "success",
                "role": role.name,
                "permissions": permissions
            })
        except UserRole.DoesNotExist:
            # Si no tiene rol, retorna permisos vacíos
            return Response({
                "status": "success",
                "role": None,
                "permissions": []
            })
