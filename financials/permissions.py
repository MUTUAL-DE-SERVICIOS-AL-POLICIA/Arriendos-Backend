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
class HasChangePaymentPermission(permissions.BasePermission):
    message = "No tienes permisos para editar pagos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('financials.change_payment')
        return has_permission
class HasViewWarrantyMovementPermission(permissions.BasePermission):
    message = "No tienes permisos para ver los movimientos de garantías"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('financials.view_warranty_movement')
        return has_permission
class HasAddWarrantyMovementPermission(permissions.BasePermission):
    message = "No tienes permisos para registrar movimientos de garantías"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('financials.add_warranty_movement')
        return has_permission
class HasDeleteWarrantyMovementPermission(permissions.BasePermission):
    message = "No tienes permisos para borrar movimientos de garantías"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('financials.delete_warranty_movement')
        return has_permission
