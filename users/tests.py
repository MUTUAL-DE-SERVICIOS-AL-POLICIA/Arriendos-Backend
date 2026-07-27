import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from roles.models import Role, UserRole


@pytest.mark.django_db
class TestUserAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        self.client.force_authenticate(user=self.user)

    def test_user_toggle_activation(self):
        user = User.objects.create_user(username='toggleme', password='pass123')
        assert user.is_active is True
        response = self.client.delete(f'/api/users/state/{user.id}')
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.is_active is False

    def test_user_toggle_reactivate(self):
        user = User.objects.create_user(username='reactivate', password='pass123', is_active=False)
        assert user.is_active is False
        response = self.client.delete(f'/api/users/state/{user.id}')
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.is_active is True

    def test_assign_role(self):
        role = Role.objects.create(name='Operador')
        user = User.objects.create_user(username='assignme', password='pass123')
        data = {'user_id': user.id, 'role_id': role.id}
        response = self.client.post('/api/roles/assign/', data, format='json')
        assert response.status_code == 201
        assert UserRole.objects.filter(user=user, role=role).exists()

    def test_user_search(self):
        User.objects.create_user(username='juan', password='pass123', first_name='Juan')
        User.objects.create_user(username='pedro', password='pass123', first_name='Pedro')
        response = self.client.get('/api/users/?search=Juan')
        assert response.status_code == 200
        assert len(response.data['users']) == 1
        assert response.data['users'][0]['first_name'] == 'Juan'

    def test_user_search_no_results(self):
        User.objects.create_user(username='juan', password='pass123', first_name='Juan')
        response = self.client.get('/api/users/?search=inexistente')
        assert response.status_code == 200
        assert len(response.data['users']) == 0

    def test_cannot_deactivate_self(self):
        response = self.client.delete(f'/api/users/state/{self.user.id}')
        assert response.status_code == 400
        self.user.refresh_from_db()
        assert self.user.is_active is True

    def test_cannot_deactivate_superuser(self):
        superuser = User.objects.create_superuser(username='other_admin', password='pass123')
        response = self.client.delete(f'/api/users/state/{superuser.id}')
        assert response.status_code == 400
