from rest_framework import permissions

class HasViewPaymenttPermission(permissions.BasePermission):
    message = "No tienes permisos para ver los pagos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('financials.view_payment')
        return has_permission
class HasAddPaymenttPermission(permissions.BasePermission):
    message = "No tienes permisos para registrar pagos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('financials.add_payment')
        return has_permission
class HasDeletePaymenttPermission(permissions.BasePermission):
    message = "No tienes permisos para borrar pagos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('financials.delete_payment')
        return has_permission