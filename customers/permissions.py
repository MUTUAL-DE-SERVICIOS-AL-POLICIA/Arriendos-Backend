from rest_framework import permissions

class HasViewCustomerPermission(permissions.BasePermission):
    message = "No tienes permisos para ver los clientes"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('customers.view_customer')
        return has_permission
class HasAddCustomerPermission(permissions.BasePermission):
    message = "No tienes permisos para crear clientes"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('customers.add_customer')
        return has_permission
class HasChangeCustomerPermission(permissions.BasePermission):
    message = "No tienes permisos para editar clientes"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('customers.change_customer')
        return has_permission

class HasViewCustomerTypePermission(permissions.BasePermission):
    message = "No tienes permisos para ver tipo clientes"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('customers.view_customer_type')
        return has_permission
class HasAddCustomerTypePermission(permissions.BasePermission):
    message = "No tienes permisos para crear tipo clientes"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('customers.add_customer_type')
        return has_permission
class HasChangeCustomerTypePermission(permissions.BasePermission):
    message = "No tienes permisos para editar tipo clientes"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('customers.change_customer_type')
        return has_permission