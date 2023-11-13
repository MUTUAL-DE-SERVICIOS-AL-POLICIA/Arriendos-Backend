
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

class HasAddHourRangePermission(permissions.BasePermission):
    message = "No tienes permisos para crear rangos de hora"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.add_hourrange')
        return has_permission
class HasViewHourRangePermission(permissions.BasePermission):
    message = "No tienes permisos para ver los rangos de hora"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.view_hourrange')
        return has_permission
class HasChangeHourRangePermission(permissions.BasePermission):
    message = "No tienes permisos para editar rangos de hora"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.change_hourrange')
        return has_permission
class HasDeleteHourRangePermission(permissions.BasePermission):
    message = "No tienes permisos para borrar los rangos de hora"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.delete_hourrange')
        return has_permission

class HasAddPricePermission(permissions.BasePermission):
    message = "No tienes permisos para crear los precios"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.add_price')
        return has_permission
class HasViewPricePermission(permissions.BasePermission):
    message = "No tienes permisos para ver los precios"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.view_price')
        return has_permission
class HasChangePricePermission(permissions.BasePermission):
    message = "No tienes permisos para editar precios"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.change_price')
        return has_permission
class HasDeletePricePermission(permissions.BasePermission):
    message = "No tienes permisos para borrar precios"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.delete_price')
        return has_permission

class HasAddAdditionalHourPermission(permissions.BasePermission):
    message = "No tienes permisos para crear precios de horas adicionales"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.add_price_additional_hour')
        return has_permission
class HasViewAdditionalHourPermission(permissions.BasePermission):
    message = "No tienes permisos para ver las precios de horas adicionales"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.view_price_additional_hour')
        return has_permission
class HasChangeAdditionalHourPermission(permissions.BasePermission):
    message = "No tienes permisos para editar precios de horas adicionales"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.change_price_additional_hour')
        return has_permission
class HasDeleteAdditionalHourPermission(permissions.BasePermission):
    message = "No tienes permisos para borrar precios de horas adicionales"
    def has_permission(self, request, view):
        has_permission = request.user.has_perm('products.delete_price_additional_hour')
        return has_permission