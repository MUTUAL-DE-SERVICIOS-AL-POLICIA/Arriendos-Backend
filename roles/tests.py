"""
Tests de comportamiento para roles/permissions.py y roles/views.py

Comportamientos críticos cubiertos:
- Superuser bypass de todos los permisos RBAC
- Usuario sin rol recibe 403
- Rol inactivo bloquea acceso
- View sin rbac_module permite acceso a cualquier autenticado
- Mapeo de métodos HTTP a acciones (GET=view, POST=add, etc.)
- Solo Administrador puede crear/editar/eliminar roles

¿Qué debo romper para que estos tests fallen?
- Quitar el bypass de superuser en HasModulePermission
- Cambiar la lógica de UserRole.DoesNotExist
- Quitar el check de role.is_active
- Cambiar action_map en HasModulePermission
"""

import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from roles.models import Module, Permission, Role, RolePermission, UserRole


def _grant_permission(role, module_codename, perm_codename):
    """Otorga un permiso específico a un rol."""
    module, _ = Module.objects.get_or_create(
        codename=module_codename, defaults={'name': module_codename}
    )
    perm, _ = Permission.objects.get_or_create(
        codename=perm_codename, defaults={'name': perm_codename}
    )
    rp, _ = RolePermission.objects.get_or_create(role=role, module=module)
    rp.permissions.add(perm)


@pytest.mark.django_db
class TestSuperuserBypass:
    """Tests que verifican que el superuser bypasea todo RBAC."""

    def test_superuser_bypasses_rbac_on_any_module(self):
        """Superuser accede a cualquier módulo sin permisos RBAC."""
        admin = User.objects.create_superuser(username='superadmin', password='pass123')
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.get('/api/product/')

        assert response.status_code == 200

    def test_superuser_can_list_roles_without_permission(self):
        """Superuser puede listar roles sin tener permiso explícito."""
        admin = User.objects.create_superuser(username='superadmin', password='pass123')
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.get('/api/roles/')

        assert response.status_code == 200


@pytest.mark.django_db
class TestUserRoleRequired:
    """Tests que verifican que se requiere rol asignado."""

    def setup_method(self):
        self.client = APIClient()

    def test_user_without_role_gets_403(self):
        """Usuario autenticado sin rol asignado recibe 403."""
        norole = User.objects.create_user(username='norole', password='pass123')
        self.client.force_authenticate(user=norole)

        response = self.client.get('/api/product/')

        assert response.status_code == 403

    def test_inactive_role_blocks_access(self):
        """Rol inactivo bloquea acceso (403)."""
        user = User.objects.create_user(username='inactive', password='pass123')
        role = Role.objects.create(name='TestRole', is_active=False)
        UserRole.objects.create(user=user, role=role)
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/product/')

        assert response.status_code == 403


@pytest.mark.django_db
class TestNoRbacModule:
    """Tests que verifican el comportamiento cuando no hay rbac_module."""

    def test_view_without_rbac_module_allows_any_authenticated(self):
        """View sin rbac_module permite acceso a cualquier usuario autenticado."""
        user = User.objects.create_user(username='basic', password='pass123')
        client = APIClient()
        client.force_authenticate(user=user)

        # MyPermissions_View no tiene rbac_module, solo IsAuthenticated
        response = client.get('/api/roles/my-permissions/')

        assert response.status_code == 200
        assert response.data['role'] is None
        assert response.data['permissions'] == []


@pytest.mark.django_db
class TestPermissionMapping:
    """Tests que verifican el mapeo de métodos HTTP a acciones."""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='tester', password='pass123')
        self.role = Role.objects.create(name='TestRole')
        self.client.force_authenticate(user=self.user)
        UserRole.objects.create(user=self.user, role=self.role)

    def test_get_maps_to_view_permission(self):
        """GET requiere permiso 'view' sobre el módulo."""
        _grant_permission(self.role, 'products', 'view')

        response = self.client.get('/api/product/')

        assert response.status_code == 200

    def test_get_without_view_permission_returns_403(self):
        """GET sin permiso 'view' retorna 403."""
        _grant_permission(self.role, 'products', 'add')

        response = self.client.get('/api/product/')

        assert response.status_code == 403

    def test_post_assign_requires_admin_role(self):
        """POST /api/roles/assign/ requiere rol Administrador."""
        user = User.objects.create_user(username='admin_post', password='pass123')
        admin_role = Role.objects.create(name='Operador')
        _grant_permission(admin_role, 'users', 'add')
        UserRole.objects.create(user=user, role=admin_role)
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/roles/assign/', {
            'user_id': 999, 'role_id': 999
        }, format='json')

        assert response.status_code == 403

    def test_delete_user_requires_admin_role(self):
        """DELETE /api/users/state/<pk> requiere rol Operador/Admin."""
        operador = User.objects.create_user(username='operador_user', password='pass123')
        operador_role = Role.objects.create(name='Operador')
        _grant_permission(operador_role, 'users', 'delete')
        UserRole.objects.create(user=operador, role=operador_role)
        admin_target = User.objects.create_user(username='admin_target', password='pass123')
        admin_target_role = Role.objects.create(name='Administrador')
        UserRole.objects.create(user=admin_target, role=admin_target_role)
        self.client.force_authenticate(user=operador)

        response = self.client.delete(f'/api/users/state/{admin_target.id}')

        assert response.status_code == 403


@pytest.mark.django_db
class TestRoleAdminOnly:
    """Tests que verifican que solo Administrador puede gestionar roles."""

    def setup_method(self):
        self.client = APIClient()

    def test_non_admin_cannot_create_role(self):
        """Usuario no-admin no puede crear roles (403)."""
        user = User.objects.create_user(username='noadmin', password='pass123')
        role = Role.objects.create(name='Operador')
        _grant_permission(role, 'users', 'add')
        UserRole.objects.create(user=user, role=role)
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/roles/', {
            'name': 'NuevoRol', 'description': 'Test', 'is_active': True,
            'permissions_data': []
        }, format='json')

        assert response.status_code == 403

    def test_non_admin_cannot_edit_role(self):
        """Usuario no-admin no puede editar roles (403)."""
        user = User.objects.create_user(username='noadmin', password='pass123')
        role = Role.objects.create(name='Operador')
        _grant_permission(role, 'users', 'change')
        UserRole.objects.create(user=user, role=role)
        self.client.force_authenticate(user=user)

        target_role = Role.objects.create(name='Target')

        response = self.client.patch(f'/api/roles/{target_role.id}', {
            'name': 'Modificado'
        }, format='json')

        assert response.status_code == 403

    def test_non_admin_cannot_delete_role(self):
        """Usuario no-admin no puede eliminar roles (403)."""
        user = User.objects.create_user(username='noadmin', password='pass123')
        role = Role.objects.create(name='Operador')
        _grant_permission(role, 'users', 'delete')
        UserRole.objects.create(user=user, role=role)
        self.client.force_authenticate(user=user)

        target_role = Role.objects.create(name='ToDelete')

        response = self.client.delete(f'/api/roles/{target_role.id}')

        assert response.status_code == 403

    def test_admin_can_create_role(self):
        """Administrador SÍ puede crear roles."""
        admin = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=admin)

        response = self.client.post('/api/roles/', {
            'name': 'NuevoRol', 'description': 'Test', 'is_active': True,
            'permissions_data': []
        }, format='json')

        assert response.status_code == 201
        assert Role.objects.filter(name='NuevoRol').exists()

    def test_role_delete_with_users_fails(self):
        """No se puede eliminar un rol que tiene usuarios asignados."""
        admin = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=admin)

        role = Role.objects.create(name='HasUsers')
        user = User.objects.create_user(username='testuser', password='pass123')
        UserRole.objects.create(user=user, role=role)

        response = self.client.delete(f'/api/roles/{role.id}')

        assert response.status_code == 400
        assert Role.objects.filter(name='HasUsers').exists()

    def test_my_permissions_returns_correct_format(self):
        """MyPermissions retorna el rol y permisos en formato correcto."""
        user = User.objects.create_user(username='withperms', password='pass123')
        role = Role.objects.create(name='Operador')
        UserRole.objects.create(user=user, role=role)

        _grant_permission(role, 'products', 'view')

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/roles/my-permissions/')

        assert response.status_code == 200
        assert response.data['role'] == 'Operador'
        assert 'products.view' in response.data['permissions']
