"""
Modelos RBAC (Role-Based Access Control) - Control de Acceso Basado en Roles

Este modulo implementa el sistema de control de acceso basado en roles del sistema.
Permite gestionar modulos del sistema, permisos por modulo, roles con permisos
asignados, y la relacion entre usuarios y roles.

Estructura:
- Module: Modulos del sistema (Productos, Inmuebles, Clientes, etc.)
- Permission: Permisos disponibles (Ver, Crear, Editar, Eliminar)
- Role: Roles definidos en el sistema (Administrador, Gerente, etc.)
- RolePermission: Asociacion de permisos por modulo para cada rol
- UserRole: Asignacion de rol a un usuario (1 usuario = 1 rol)

Autor: Dilan Torrez
Fecha: 2026
"""

from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Module(models.Model):
    """
    Representa un modulo o area funcional del sistema.

    Cada modulo agrupa funcionalidades relacionadas y permite asignar
    permisos especificos sobre el. Por ejemplo, el modulo 'products'
    controla el acceso a la gestion de productos, tarifas y precios.

    Campos:
        - name: Nombre descriptivo del modulo (ej: 'Productos')
        - codename: Codigo unico para identificar el modulo internamente (ej: 'products')
        - description: Descripcion detallada del modulo
        - is_active: Indica si el modulo esta habilitado
        - created_at: Fecha y hora de creacion
    """
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
    """
    Representa una accion que se puede realizar sobre un modulo.

    Los permisos definen las operaciones disponibles: Ver, Crear, Editar, Eliminar.
    Cada permiso se combina con un modulo para crear permisos especificos.
    Por ejemplo: 'products.view' (Ver productos), 'leases.add' (Crear arriendos).

    Campos:
        - name: Nombre descriptivo del permiso (ej: 'Ver')
        - codename: Codigo unico del permiso (ej: 'view', 'add', 'change', 'delete')
        - description: Descripcion del permiso
        - created_at: Fecha y hora de creacion
    """
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
    """
    Representa un rol del sistema que agrupa permisos.

    Un rol define un conjunto de permisos que se pueden asignar a usuarios.
    Por ejemplo, el rol 'Operador' puede tener permisos de vista y creacion
    de arriendos, pero no de eliminacion.

    Ejemplos de roles predefinidos:
        - Administrador: Acceso total al sistema
        - Gerente: Gestion completa excepto usuarios y finanzas
        - Operador: Operaciones diarias de arriendos
        - Cajero: Gestion de pagos y garantias
        - Consulta: Solo lectura en todo el sistema

    Campos:
        - name: Nombre unico del rol (ej: 'Administrador')
        - description: Descripcion del rol
        - is_active: Indica si el rol esta habilitado
        - created_at: Fecha y hora de creacion
        - updated_at: Fecha y hora de ultima actualizacion
    """
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
    """
    Asocia permisos a un rol para un modulo especifico.

    Esta tabla intermedia define que permisos tiene un rol sobre un modulo.
    Por ejemplo: El rol 'Operador' tiene permisos ['view', 'add'] sobre
    el modulo 'leases' (Arriendos).

    Cada registro representa:
    - Un rol (ej: Operador)
    - Un modulo (ej: Arriendos)
    - Una lista de permisos (ej: Ver, Crear)

    Restriccion unique_together: Un rol solo puede tener UNA configuracion
    de permisos por modulo.

    Campos:
        - role: Referencia al rol
        - module: Referencia al modulo
        - permissions: Lista de permisos otorgados en este modulo
    """
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
    """
    Asigna un rol a un usuario del sistema.

    Relacion 1:1 entre usuario y rol. Cada usuario puede tener
    UN SOLO rol asignado. Si se necesita cambiar el rol, se debe
    actualizar este registro.

    Esta relacion es fundamental para el funcionamiento del RBAC:
    1. El usuario inicia sesion
    2. Se busca su UserRole para obtener el rol asignado
    3. Se consultan los RolePermission del rol
    4. Se valida si tiene permiso para la accion solicitada

    Campos:
        - user: Usuario de Django (OneToOne relationship)
        - role: Rol asignado al usuario
        - assigned_at: Fecha y hora de asignacion del rol
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_role', verbose_name="Usuario")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="Rol")
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Asignado el")

    class Meta:
        verbose_name = "Rol de Usuario"
        verbose_name_plural = "Roles de Usuarios"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
