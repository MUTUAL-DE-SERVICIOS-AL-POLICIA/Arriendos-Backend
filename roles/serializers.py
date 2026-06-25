from rest_framework import serializers
from .models import Module, Permission, Role, RolePermission, UserRole
from django.contrib.auth.models import User


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class RolePermissionSerializer(serializers.ModelSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)
    module_codename = serializers.CharField(source='module.codename', read_only=True)
    permission_names = serializers.SerializerMethodField()

    class Meta:
        model = RolePermission
        fields = ['id', 'module', 'module_name', 'module_codename', 'permissions', 'permission_names']

    def get_permission_names(self, obj):
        return list(obj.permissions.values_list('codename', flat=True))


class RoleSerializer(serializers.ModelSerializer):
    role_permissions = RolePermissionSerializer(many=True, read_only=True)
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active', 'role_permissions', 'user_count', 'created_at', 'updated_at']

    def get_user_count(self, obj):
        return UserRole.objects.filter(role=obj).count()


class RoleCreateSerializer(serializers.ModelSerializer):
    permissions_data = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active', 'permissions_data']

    def create(self, validated_data):
        permissions_data = validated_data.pop('permissions_data', [])
        role = Role.objects.create(**validated_data)
        for item in permissions_data:
            module_id = item.get('module')
            permission_ids = item.get('permissions', [])
            role_perm = RolePermission.objects.create(role=role, module_id=module_id)
            role_perm.permissions.set(permission_ids)
        return role

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permissions_data', [])
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        if permissions_data:
            RolePermission.objects.filter(role=instance).delete()
            for item in permissions_data:
                module_id = item.get('module')
                permission_ids = item.get('permissions', [])
                role_perm = RolePermission.objects.create(role=instance, module_id=module_id)
                role_perm.permissions.set(permission_ids)
        return instance


class UserRoleSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'username', 'first_name', 'last_name', 'role', 'role_name', 'assigned_at']


class UserRoleCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("El usuario no existe")
        return value

    def validate_role_id(self, value):
        if not Role.objects.filter(id=value).exists():
            raise serializers.ValidationError("El rol no existe")
        return value

    def create(self, validated_data):
        user_role, created = UserRole.objects.update_or_create(
            user_id=validated_data['user_id'],
            defaults={'role_id': validated_data['role_id']}
        )
        return user_role


class UserWithRoleSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'role']

    def get_role(self, obj):
        try:
            user_role = UserRole.objects.get(user=obj)
            return {
                'id': user_role.role.id,
                'name': user_role.role.name,
            }
        except UserRole.DoesNotExist:
            return None
