
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