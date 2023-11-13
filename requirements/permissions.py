from rest_framework import permissions

class HasViewRequirementPermission(permissions.BasePermission):
    message = "No tienes permisos para ver los requisitos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('requirements.view_requirement')
        return has_permission
class HasAddRequirementPermission(permissions.BasePermission):
    message = "No tienes permisos para crear requisitos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('requirements.add_requirement')
        return has_permission
class HasChangeRequirementPermission(permissions.BasePermission):
    message = "No tienes permisos para editar requisitos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('requirements.change_requirement')
        return has_permission
class HasDeleteRequirementPermission(permissions.BasePermission):
    message = "No tienes permisos para borrar requisitos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('requirements.delete_requirement')
        return has_permission

class HasViewRateRequirementPermission(permissions.BasePermission):
    message = "No tienes permisos para ver las tarifas con sus requisitos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('requirements.view_raterequirement')
        return has_permission
class HasAddRateRequirementPermission(permissions.BasePermission):
    message = "No tienes permisos para crear tarifas con sus requisitos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('requirements.add_raterequirement')
        return has_permission
class HasChangeRateRequirementPermission(permissions.BasePermission):
    message = "No tienes permisos para editar las tarifas con sus requisitos"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('requirements.change_raterequirement')
        return has_permission

class HasAddRequirementDeliveredRequirementPermission(permissions.BasePermission):
    message = "No tienes permisos para crear registros de requisitos entregados"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('requirements.add_requirement_delivered')
        return has_permission
