import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestLoginAPI:
    def setup_method(self):
        self.client = APIClient()

    def test_local_login_success(self):
        User.objects.create_user(username='testuser', password='testpass123')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post('/api/login/auth/', data, format='json')
        assert response.status_code == 200
        assert 'access' in response.data

    def test_local_login_wrong_password(self):
        User.objects.create_user(username='testuser', password='testpass123')
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post('/api/login/auth/', data, format='json')
        assert response.status_code in [400, 401]

    def test_local_login_nonexistent_user(self):
        data = {'username': 'nouser', 'password': 'nopass'}
        response = self.client.post('/api/login/auth/', data, format='json')
        assert response.status_code in [400, 401]

    def test_login_empty_body(self):
        response = self.client.post('/api/login/auth/', {}, format='json')
        assert response.status_code in [400, 401]
