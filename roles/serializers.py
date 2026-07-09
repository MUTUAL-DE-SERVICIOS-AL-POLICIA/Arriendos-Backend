"""
Serializadores RBAC para Django REST Framework.

Este modulo contiene los serializadores necesarios para la API
del sistema de control de acceso basado en roles (RBAC).

Serializadores incluidos:
- ModuleSerializer: Serializador para modulos
- PermissionSerializer: Serializador para permisos
- RolePermissionSerializer: Serializador para permisos de rol con detalles
- RoleSerializer: Serializador completo de rol con permisos
- RoleCreateSerializer: Serializador para crear/editar roles
- UserRoleSerializer: Serializador para asignacion de roles a usuarios
- UserRoleCreateSerializer: Serializador para crear asignaciones de roles
- UserWithRoleSerializer: Serializador de usuario con su rol

Autor: Dilan Torrez
Fecha: 2026
"""

from rest_framework import serializers
from .models import Module, Permission, Role, RolePermission, UserRole
from django.contrib.auth import get_user_model
User = get_user_model()


class ModuleSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Module.

    Serializa todos los campos del modulo para ser utilizados
    en la API de gestion de roles y permisos.
    """
    class Meta:
        model = Module
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Permission.

    Serializa todos los campos del permiso para ser utilizados
    en la API de gestion de roles y permisos.
    """
    class Meta:
        model = Permission
        fields = '__all__'


class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo RolePermission con detalles.

    Incluye información adicional del módulo y los nombres de los permisos
    para facilitar la visualización en el frontend.

    Campos adicionales:
        - module_name: Nombre del módulo (ej: 'Productos')
        - module_codename: Código del módulo (ej: 'products')
        - permission_names: Lista de códigos de permisos (ej: ['view', 'add'])
    """
    module_name = serializers.CharField(source='module.name', read_only=True)
    module_codename = serializers.CharField(source='module.codename', read_only=True)
    permission_names = serializers.SerializerMethodField()

    class Meta:
        model = RolePermission
        fields = ['id', 'module', 'module_name', 'module_codename', 'permissions', 'permission_names']

    def get_permission_names(self, obj):
        """Retorna una lista con los códigos de los permisos asignados."""
        return list(obj.permissions.values_list('codename', flat=True))


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializador completo del modelo Role.

    Incluye los permisos asignados al rol y la cantidad de usuarios
    que tienen ese rol. Utilizado para listar roles y mostrar detalles.

    Campos adicionales:
        - role_permissions: Lista de permisos por módulo ( RolePermissionSerializer )
        - user_count: Cantidad de usuarios con este rol
    """
    role_permissions = RolePermissionSerializer(many=True, read_only=True)
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active', 'role_permissions', 'user_count', 'created_at', 'updated_at']

    def get_user_count(self, obj):
        """Cuenta cuántos usuarios tienen asignado este rol."""
        return UserRole.objects.filter(role=obj).count()


class RoleCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para crear y actualizar roles.

    Maneja la creación de roles con sus permisos asociados.
    El campo permissions_data permite definir qué permisos tiene
    el rol sobre cada módulo.

    Estructura de permissions_data:
    [
        {
            "module": 1,  # ID del módulo
            "permissions": [1, 2, 3]  # IDs de los permisos
        },
        ...
    ]

    Métodos:
        - create: Crea un nuevo rol con sus permisos
        - update: Actualiza un rol existente (reemplaza permisos)
    """
    permissions_data = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active', 'permissions_data']

    def create(self, validated_data):
        """Crea un nuevo rol y asigna sus permisos por módulo."""
        permissions_data = validated_data.pop('permissions_data', [])
        role = Role.objects.create(**validated_data)
        for item in permissions_data:
            module_id = item.get('module')
            permission_ids = item.get('permissions', [])
            role_perm = RolePermission.objects.create(role=role, module_id=module_id)
            role_perm.permissions.set(permission_ids)
        return role

    def update(self, instance, validated_data):
        """Actualiza un rol existente y reemplaza sus permisos."""
        permissions_data = validated_data.pop('permissions_data', [])
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        if permissions_data:
            # Eliminar permisos anteriores y crear nuevos
            RolePermission.objects.filter(role=instance).delete()
            for item in permissions_data:
                module_id = item.get('module')
                permission_ids = item.get('permissions', [])
                role_perm = RolePermission.objects.create(role=instance, module_id=module_id)
                role_perm.permissions.set(permission_ids)
        return instance


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo UserRole con información del usuario y rol.

    Incluye datos del usuario (nombre, apellido, username) y del rol
    para facilitar la visualización en la interfaz de gestión de usuarios.

    Campos adicionales (read-only):
        - username: Nombre de usuario
        - first_name: Nombre del usuario
        - last_name: Apellido del usuario
        - role_name: Nombre del rol asignado
    """
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'username', 'first_name', 'last_name', 'role', 'role_name', 'assigned_at']


class UserRoleCreateSerializer(serializers.Serializer):
    """
    Serializador para crear o actualizar la asignación de rol a un usuario.

    Valida que:
    - El usuario exista en el sistema
    - El rol exista en el sistema
    - Un usuario no pueda asignarse un rol a sí mismo (previene manipulación)

    Si el usuario ya tiene un rol asignado, lo actualiza.
    Si no tiene rol, crea una nueva asignación.

    Campos:
        - user_id: ID del usuario
        - role_id: ID del rol a asignar
    """
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate_user_id(self, value):
        """Valida que el usuario exista en la base de datos."""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("El usuario no existe")
        return value

    def validate_role_id(self, value):
        """Valida que el rol exista en la base de datos."""
        if not Role.objects.filter(id=value).exists():
            raise serializers.ValidationError("El rol no existe")
        return value

    def validate(self, data):
        """
        Validación global: previene que un usuario se asigne un rol a sí mismo.
        Esto es un control de seguridad para evitar que usuarios manipulen
        sus propios permisos.
        """
        request = self.context.get('request')
        if request and data.get('user_id') == request.user.id:
            raise serializers.ValidationError("No puedes asignarte un rol a ti mismo")
        return data

    def create(self, validated_data):
        """
        Crea o actualiza la asignación de rol a un usuario.
        Usa update_or_create para manejar ambos casos.
        """
        user_role, created = UserRole.objects.update_or_create(
            user_id=validated_data['user_id'],
            defaults={'role_id': validated_data['role_id']}
        )
        return user_role


class UserWithRoleSerializer(serializers.ModelSerializer):
    """
    Serializador de usuario que incluye información de su rol.

    Utilizado para listar usuarios mostrando su rol asignado.
    Si el usuario no tiene rol, retorna role=None.

    Campos adicionales:
        - role: Objeto con id y name del rol asignado, o None si no tiene rol
    """
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'role']

    def get_role(self, obj):
        """
        Obtiene el rol del usuario si tiene uno asignado.
        Retorna un diccionario con id y name, o None si no tiene rol.
        """
        try:
            user_role = UserRole.objects.get(user=obj)
            return {
                'id': user_role.role.id,
                'name': user_role.role.name,
            }
        except UserRole.DoesNotExist:
            return None
