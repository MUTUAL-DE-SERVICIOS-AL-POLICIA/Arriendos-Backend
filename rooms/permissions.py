# en tu archivo permissions.py

from rest_framework import permissions

class HasViewPropertyPermission(permissions.BasePermission):
    message = "No tienes permisos para ver las Propiedades"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('rooms.view_property')
        return has_permission
class HasAddPropertyPermission(permissions.BasePermission):
    message = "No tienes permiso para crear Propiedades"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('rooms.add_property')
        return has_permission
class HasChangePropertyPermission(permissions.BasePermission):
    message = "No tienes permisos para editar las Propiedades"
    def has_permission(self, request, view):
        return request.user.has_perm('rooms.change_property')
class HasDeletePropertyPermission(permissions.BasePermission):
    message = "No tienes permisos para borrar las Propiedades"
    def has_permission(self, request, view):
        return request.user.has_perm('rooms.delete_property')
