import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from threadlocals.threadlocals import set_thread_variable


@pytest.fixture(autouse=True)
def _clear_threadlocals():
    set_thread_variable('thread_user', None)
    yield
    set_thread_variable('thread_user', None)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='admin',
        password='adminpass123',
        email='admin@example.com'
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
