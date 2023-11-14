
from rest_framework import permissions

class HasViewRentalStatePermission(permissions.BasePermission):
    message = "No tienes permisos para ver los estados de arriendo"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('leases.view_rental_state')
        return has_permission
class HasAddRentalStatePermission(permissions.BasePermission):
    message = "No tienes permisos para crear estados de arriendo"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('leases.add_rental_state')
        return has_permission

class HasViewSelectedProductPermission(permissions.BasePermission):
    message = "No tienes permisos para ver los productos seleccionados"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('leases.view_selected_product')
        return has_permission
class HasChangeSelectedProductPermission(permissions.BasePermission):
    message = "No tienes permisos para ver los productos seleccionados"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('leases.change_selected_product')
        return has_permission

class HasViewRentalPermission(permissions.BasePermission):
    message = "No tienes permisos para ver los arriendos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('leases.view_rental')
        return has_permission
class HasAddRentalPermission(permissions.BasePermission):
    message = "No tienes permisos para crear arriendos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('leases.add_rental')
        return has_permission
class HasChangeRentalPermission(permissions.BasePermission):
    message = "No tienes permisos para editar los arriendos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('leases.change_rental')
        return has_permission

class HasViewAdditionalHourAppliedPermission(permissions.BasePermission):
    message = "No tienes permisos para ver las horas adicionales"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('leases.view_additional_hour_applied')
        return has_permission
class HasAddAdditionalHourAppliedPermission(permissions.BasePermission):
    message = "No tienes permisos para crear horas adicionales"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('leases.add_additional_hour_applied')
        return has_permission
class HasDeleteAdditionalHourAppliedPermission(permissions.BasePermission):
    message = "No tienes permisos para eliminar horas adicionales"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('leases.delete_additional_hour_applied')
        return has_permission