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
import logging

security_logger = logging.getLogger('security')


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
    "No tienes permiso de [accion] en el modulo [modulo]"
    """
    # Traducción de módulos del sistema (codename → nombre en español)
    MODULE_NAMES = {
        'products': 'Productos',
        'rooms': 'Ambientes',
        'customers': 'Clientes',
        'leases': 'Arriendos',
        'financials': 'Finanzas',
        'requirements': 'Requisitos',
        'users': 'Usuarios',
        'records': 'Registros',
        'documents': 'Documentos',
        'plans': 'Planes',
    }

    # Traducción de acciones (codename → nombre en español)
    ACTION_NAMES = {
        'view': 'ver',
        'add': 'crear',
        'change': 'editar',
        'delete': 'eliminar',
        'export': 'exportar',
    }

    message = "No tienes permisos para realizar esta accion"

    def _get_module_name(self, codename):
        return self.MODULE_NAMES.get(codename, codename)

    def _get_action_name(self, codename):
        return self.ACTION_NAMES.get(codename, codename)

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        rbac_module = getattr(view, 'rbac_module', None)
        if not rbac_module:
            return True

        try:
            user_role = UserRole.objects.get(user=user)
            role = user_role.role
            if not role.is_active:
                module_name = self._get_module_name(rbac_module)
                self.message = f"No tienes permisos para acceder al módulo '{module_name}'"
                security_logger.warning(f"ACCESS_DENY: usuario={user.username} modulo={rbac_module} razon=rol_inactivo")
                return False
        except UserRole.DoesNotExist:
            module_name = self._get_module_name(rbac_module)
            self.message = f"No tienes permisos para acceder al módulo '{module_name}'"
            security_logger.warning(f"ACCESS_DENY: usuario={user.username} modulo={rbac_module} razon=sin_rol")
            return False

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

        role_perms = RolePermission.objects.filter(role=role, module__codename=rbac_module)

        for rp in role_perms:
            if rp.permissions.filter(codename=required_action).exists():
                return True

        module_name = self._get_module_name(rbac_module)
        action_name = self._get_action_name(required_action)
        self.message = f"No tienes permiso de '{action_name}' en el módulo '{module_name}'"
        security_logger.warning(f"ACCESS_DENY: usuario={user.username} modulo={rbac_module} accion={required_action} razon=sin_permiso")
        return False

