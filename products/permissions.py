
from rest_framework import permissions

class HasViewRatePermission(permissions.BasePermission):
    message = "No tienes permisos para ver las tarifas"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.view_rate')
        return has_permission
