from django.db import models
from django.contrib.auth.models import User


class Module(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del modulo")
    codename = models.CharField(max_length=50, unique=True, verbose_name="Codigo")
    description = models.TextField(blank=True, verbose_name="Descripcion")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modulo"
        verbose_name_plural = "Modulos"
        ordering = ['name']

    def __str__(self):
        return self.name


class Permission(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del permiso")
    codename = models.CharField(max_length=50, unique=True, verbose_name="Codigo")
    description = models.TextField(blank=True, verbose_name="Descripcion")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del rol")
    description = models.TextField(blank=True, verbose_name="Descripcion")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['name']

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions', verbose_name="Rol")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name="Modulo")
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name="Permisos")

    class Meta:
        verbose_name = "Permiso de Rol"
        verbose_name_plural = "Permisos de Roles"
        unique_together = ['role', 'module']

    def __str__(self):
        perms = ', '.join([p.codename for p in self.permissions.all()])
        return f"{self.role.name} - {self.module.name}: {perms}"


class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_role', verbose_name="Usuario")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="Rol")
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Asignado el")

    class Meta:
        verbose_name = "Rol de Usuario"
        verbose_name_plural = "Roles de Usuarios"

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
