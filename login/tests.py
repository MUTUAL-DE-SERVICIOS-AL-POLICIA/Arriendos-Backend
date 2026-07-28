import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestLocalLoginSuccess:
    """POST /api/login/auth/ — login exitoso"""

    def setup_method(self):
        self.client = APIClient()

    def test_login_success_returns_tokens(self):
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post('/api/login/auth/', {
            'username': 'testuser', 'password': 'testpass123'
        }, format='json')
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert len(response.data['access']) > 0

    def test_superuser_login_returns_tokens(self):
        User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        response = self.client.post('/api/login/auth/', {
            'username': 'admin', 'password': 'admin123'
        }, format='json')
        assert response.status_code == 200
        assert 'access' in response.data

    def test_login_wrong_password_returns_401(self):
        User.objects.create_user(username='testuser', password='correct')
        response = self.client.post('/api/login/auth/', {
            'username': 'testuser', 'password': 'wrongpass'
        }, format='json')
        assert response.status_code == 401

    def test_login_nonexistent_user_returns_401(self):
        response = self.client.post('/api/login/auth/', {
            'username': 'nobody', 'password': 'nopass'
        }, format='json')
        assert response.status_code == 401

    def test_login_missing_fields_returns_401(self):
        response = self.client.post('/api/login/auth/', {}, format='json')
        assert response.status_code == 401

    def test_login_returns_user_data(self):
        User.objects.create_user(username='testuser', password='pass123')
        response = self.client.post('/api/login/auth/', {
            'username': 'testuser', 'password': 'pass123'
        }, format='json')
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_inactive_user_returns_401(self):
        User.objects.create_user(username='inactive', password='pass123', is_active=False)
        response = self.client.post('/api/login/auth/', {
            'username': 'inactive', 'password': 'pass123'
        }, format='json')
        assert response.status_code == 401
