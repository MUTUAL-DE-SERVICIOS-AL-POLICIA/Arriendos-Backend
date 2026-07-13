import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from roles.models import Module, Permission, Role, RolePermission, UserRole


@pytest.mark.django_db
class TestRoleModels:
    def test_role_creation(self):
        role = Role.objects.create(name='Admin', description='Administrator')
        assert role.name == 'Admin'
        assert str(role) == 'Admin'

    def test_module_creation(self):
        module = Module.objects.create(name='Products', codename='products')
        assert module.codename == 'products'
        assert str(module) == 'Products'

    def test_permission_creation(self):
        perm = Permission.objects.create(name='View', codename='view')
        assert perm.codename == 'view'
        assert str(perm) == 'View'

    def test_role_permission_assignment(self):
        role = Role.objects.create(name='Operator')
        module = Module.objects.create(name='Products', codename='products')
        perm = Permission.objects.create(name='View', codename='view')
        rp = RolePermission.objects.create(role=role, module=module)
        rp.permissions.add(perm)
        assert rp.role == role
        assert rp.module == module
        assert rp.permissions.count() == 1
        assert 'Operator' in str(rp)
        assert 'Products' in str(rp)
        assert 'view' in str(rp)

    def test_user_role_assignment(self):
        user = User.objects.create_user(username='testuser', password='test123')
        role = Role.objects.create(name='Operator')
        ur = UserRole.objects.create(user=user, role=role)
        assert ur.user == user
        assert ur.role == role
        assert 'testuser' in str(ur)
        assert 'Operator' in str(ur)


@pytest.mark.django_db
class TestRoleAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_role_list(self):
        Role.objects.create(name='Admin')
        Role.objects.create(name='Operator')
        response = self.client.get('/api/roles/')
        assert response.status_code == 200
        assert response.data['total'] == 2

    def test_role_create(self):
        data = {'name': 'NewRole', 'description': 'Test role'}
        response = self.client.post('/api/roles/', data, format='json')
        assert response.status_code == 201
        assert Role.objects.count() == 1

    def test_role_update(self):
        role = Role.objects.create(name='OldName')
        response = self.client.patch(f'/api/roles/{role.id}', {'name': 'NewName'}, format='json')
        assert response.status_code == 200
        role.refresh_from_db()
        assert role.name == 'NewName'

    def test_role_delete(self):
        role = Role.objects.create(name='ToDelete')
        response = self.client.delete(f'/api/roles/{role.id}')
        assert response.status_code == 200
        assert Role.objects.count() == 0

    def test_role_delete_with_users_fails(self):
        role = Role.objects.create(name='HasUsers')
        user = User.objects.create_user(username='testuser', password='test123')
        UserRole.objects.create(user=user, role=role)
        response = self.client.delete(f'/api/roles/{role.id}')
        assert response.status_code == 400
        assert Role.objects.count() == 1

    def test_module_list(self):
        Module.objects.create(name='Products', codename='products')
        response = self.client.get('/api/roles/modules/')
        assert response.status_code == 200

    def test_permission_list(self):
        Permission.objects.create(name='View', codename='view')
        response = self.client.get('/api/roles/permissions/')
        assert response.status_code == 200

    def test_my_permissions(self):
        response = self.client.get('/api/roles/my-permissions/')
        assert response.status_code == 200
        assert response.data['role'] is None

    def test_assignments_list(self):
        user = User.objects.create_user(username='testuser', password='test123')
        role = Role.objects.create(name='Admin')
        UserRole.objects.create(user=user, role=role)
        response = self.client.get('/api/roles/assignments/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestPermissionGating:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='consulta', password='test123')
        self.role = Role.objects.create(name='Consulta')
        self.client.force_authenticate(user=self.user)
        UserRole.objects.create(user=self.user, role=self.role)

    def test_user_with_view_permission_can_list(self):
        module = Module.objects.create(name='Products', codename='products')
        perm = Permission.objects.create(name='View', codename='view')
        rp = RolePermission.objects.create(role=self.role, module=module)
        rp.permissions.add(perm)
        response = self.client.get('/api/product/')
        assert response.status_code == 200

    def test_user_without_add_permission_cannot_create(self):
        module = Module.objects.create(name='Products', codename='products')
        perm = Permission.objects.create(name='View', codename='view')
        rp = RolePermission.objects.create(role=self.role, module=module)
        rp.permissions.add(perm)
        response = self.client.post('/api/product/', {'day': ['LUNES']}, format='json')
        assert response.status_code == 403

    def test_superuser_bypasses_all_permissions(self):
        self.client.force_authenticate(user=self.user)
        admin = User.objects.create_superuser(username='superadmin', password='admin123')
        self.client.force_authenticate(user=admin)
        response = self.client.get('/api/product/')
        assert response.status_code == 200

    def test_user_without_role_gets_403(self):
        norole = User.objects.create_user(username='norole', password='test123')
        self.client.force_authenticate(user=norole)
        response = self.client.get('/api/product/')
        assert response.status_code == 403
