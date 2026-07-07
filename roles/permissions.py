"""
Clases de permisos RBAC para Django REST Framework.

Este modulo contiene la clase HasModulePermission que se utiliza
como permiso generico en todas las vistas protegidas por RBAC.

Uso en vistas:
    class MiVista(generics.ListAPIView):
        permission_classes = [IsAuthenticated, HasModulePermission]
        rbac_module = 'products'  # Codigo del modulo a validar

Flujo de validacion:
1. Verificar que el usuario este autenticado
2. Obtener el modulo de la vista (rbac_module)
3. Buscar el rol asignado al usuario (UserRole)
4. Verificar que el rol este activo
5. Mapear el metodo HTTP a la accion requerida (GET=view, POST=add, etc.)
6. Validar que el rol tenga el permiso sobre el modulo

Autor: Dilan Torrez
Fecha: 2026
"""

from rest_framework import permissions
from .models import UserRole, RolePermission


class HasModulePermission(permissions.BasePermission):
    """
    Permiso generico que valida si el usuario tiene permiso sobre un modulo.

    Este permiso reemplaza todas las clases de permisos anteriores y
    proporciona una forma estandarizada de controlar el acceso a las vistas.

    Requisitos:
        - La vista debe definir: rbac_module = 'modulo_codename'
        - El usuario debe tener un rol asignado (UserRole)
        - El rol debe estar activo

    Ejemplo:
        class Product_Api(generics.GenericAPIView):
            permission_classes = [IsAuthenticated, HasModulePermission]
            rbac_module = 'products'

    Si el usuario no tiene permiso, retorna HTTP 403 Forbidden con el mensaje:
    "No tienes permisos para realizar esta accion"
    """
    message = "No tienes permisos para realizar esta accion"

    def has_permission(self, request, view):
        # Obtener el usuario de la peticion
        user = request.user

        # Verificar que el usuario este autenticado
        if not user or not user.is_authenticated:
            return False

        # Obtener el modulo configurado en la vista
        # Si no tiene rbac_module, permitir acceso (para vistas publicas)
        rbac_module = getattr(view, 'rbac_module', None)
        if not rbac_module:
            return True

        # Buscar el rol asignado al usuario
        try:
            user_role = UserRole.objects.get(user=user)
            role = user_role.role
            # Verificar que el rol este activo
            if not role.is_active:
                return False
        except UserRole.DoesNotExist:
            # Si el usuario no tiene rol, denegar acceso
            return False

        # Mapear el metodo HTTP a la accion requerida
        # GET -> view (Ver), POST -> add (Crear), PUT/PATCH -> change (Editar),
        # DELETE -> delete (Eliminar)
        # Si la vista tiene rbac_export=True, usar permiso 'export' en vez de 'add' para POST
        method = request.method
        if getattr(view, 'rbac_export', False) and method == 'POST':
            required_action = 'view'
            rbac_module = 'documents'
        else:
            action_map = {
                'GET': 'view',
                'POST': 'add',
                'PUT': 'change',
                'PATCH': 'change',
                'DELETE': 'delete',
            }
            required_action = action_map.get(method, 'view')

        # Buscar los permisos del rol para el modulo especifico
        role_perms = RolePermission.objects.filter(role=role, module__codename=rbac_module)

        # Verificar si el rol tiene el permiso requerido
        for rp in role_perms:
            if rp.permissions.filter(codename=required_action).exists():
                return True

        # Si no tiene el permiso, denegar acceso
        return False

