from rest_framework import permissions

class HasViewUserPermission(permissions.BasePermission):
    message = "No tienes permisos para ver los usuarios"
    def has_permission(self, request, view):
        return request.user.has_perm('auth.view_user')