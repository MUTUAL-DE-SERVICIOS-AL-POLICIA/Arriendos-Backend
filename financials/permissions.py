from rest_framework import permissions

class HasViewPaymentPermission(permissions.BasePermission):
    message = "No tienes permisos para ver los pagos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('financials.view_payment')
        return has_permission
class HasAddPaymentPermission(permissions.BasePermission):
    message = "No tienes permisos para registrar pagos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('financials.add_payment')
        return has_permission
class HasDeletePaymentPermission(permissions.BasePermission):
    message = "No tienes permisos para borrar pagos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('financials.delete_payment')
        return has_permission