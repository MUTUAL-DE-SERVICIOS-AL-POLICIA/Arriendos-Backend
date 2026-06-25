from django.contrib import admin
from .models import Module, Permission, Role, RolePermission, UserRole


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'codename']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'created_at']
    search_fields = ['name', 'codename']


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0
    filter_horizontal = ['permissions']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    inlines = [RolePermissionInline]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_at']
    list_filter = ['role']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
