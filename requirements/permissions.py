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
