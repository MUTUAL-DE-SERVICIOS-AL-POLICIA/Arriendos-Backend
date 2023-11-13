
from rest_framework import permissions

class HasViewRatePermission(permissions.BasePermission):
    message = "No tienes permisos para ver las tarifas"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.view_rate')
        return has_permission

class HasViewProductPermission(permissions.BasePermission):
    message = "No tienes permisos para ver los productos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.view_product')
        return has_permission
class HasAddroductPermission(permissions.BasePermission):
    message = "No tienes permisos para crear productos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.add_product')
        return has_permission
class HasChangeProductPermission(permissions.BasePermission):
    message = "No tienes permisos para editar productos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.change_product')
        return has_permission