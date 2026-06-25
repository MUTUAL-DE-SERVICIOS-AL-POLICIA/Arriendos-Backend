from rest_framework import permissions
from .models import UserRole, RolePermission


class HasModulePermission(permissions.BasePermission):
    """
    Permiso generico que valida si el usuario tiene permiso sobre un modulo.
    La vista debe definir: rbac_module = 'modulo_codename'
    """
    message = "No tienes permisos para realizar esta accion"

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
                return False
        except UserRole.DoesNotExist:
            return False

        method = request.method
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

        return False


class HasRolePermission(permissions.BasePermission):
    """
    Permiso que valida si el usuario tiene un rol asignado.
    """
    message = "No tienes un rol asignado"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return UserRole.objects.filter(user=user).exists()
