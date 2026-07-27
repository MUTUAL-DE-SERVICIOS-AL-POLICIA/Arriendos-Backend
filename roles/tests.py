import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from roles.models import Module, Permission, Role, RolePermission, UserRole


@pytest.mark.django_db
class TestRoleAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_role_delete_with_users_fails(self):
        role = Role.objects.create(name='HasUsers')
        user = User.objects.create_user(username='testuser', password='test123')
        UserRole.objects.create(user=user, role=role)
        response = self.client.delete(f'/api/roles/{role.id}')
        assert response.status_code == 400
        assert Role.objects.count() == 1


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
