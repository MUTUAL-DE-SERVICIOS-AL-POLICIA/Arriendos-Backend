import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from threadlocals.threadlocals import set_thread_variable
from roles.models import Module, Permission, Role, RolePermission, UserRole


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


def _grant_permission(role, module_codename, perm_codename):
    module, _ = Module.objects.get_or_create(
        codename=module_codename, defaults={'name': module_codename}
    )
    perm, _ = Permission.objects.get_or_create(
        codename=perm_codename, defaults={'name': perm_codename}
    )
    rp, _ = RolePermission.objects.get_or_create(role=role, module=module)
    rp.permissions.add(perm)


@pytest.fixture
def rbac_admin(api_client, db):
    """Admin autenticado con rol Administrador y permisos completos."""
    admin = User.objects.create_superuser(username='rbac_admin', password='pass123')
    admin_role = Role.objects.create(name='Administrador')
    for perm in ['view', 'add', 'change', 'delete']:
        _grant_permission(admin_role, 'financials', perm)
        _grant_permission(admin_role, 'customers', perm)
        _grant_permission(admin_role, 'requirements', perm)
        _grant_permission(admin_role, 'products', perm)
        _grant_permission(admin_role, 'rooms', perm)
        _grant_permission(admin_role, 'users', perm)
        _grant_permission(admin_role, 'leases', perm)
        _grant_permission(admin_role, 'records', perm)
        _grant_permission(admin_role, 'documents', perm)
        _grant_permission(admin_role, 'plans', perm)
    UserRole.objects.create(user=admin, role=admin_role)
    api_client.force_authenticate(user=admin)
    return api_client


@pytest.fixture
def rbac_operador(api_client, db):
    """Operador autenticado con permisos limitados."""
    operador = User.objects.create_user(username='operador_test', password='pass123')
    operador_role = Role.objects.create(name='Operador')
    for perm in ['view', 'add', 'change', 'delete']:
        _grant_permission(operador_role, 'financials', perm)
        _grant_permission(operador_role, 'customers', perm)
        _grant_permission(operador_role, 'leases', perm)
        _grant_permission(operador_role, 'products', perm)
        _grant_permission(operador_role, 'requirements', perm)
        _grant_permission(operador_role, 'rooms', perm)
        _grant_permission(operador_role, 'documents', perm)
        _grant_permission(operador_role, 'plans', perm)
    UserRole.objects.create(user=operador, role=operador_role)
    api_client.force_authenticate(user=operador)
    return api_client


@pytest.fixture
def rbac_visualizador(api_client, db):
    """Visualizador autenticado solo con permiso view."""
    visualizador = User.objects.create_user(username='visualizador_test', password='pass123')
    visualizador_role = Role.objects.create(name='Visualizador')
    for module in ['financials', 'customers', 'leases', 'products', 'requirements', 'rooms', 'documents', 'plans']:
        _grant_permission(visualizador_role, module, 'view')
    UserRole.objects.create(user=visualizador, role=visualizador_role)
    api_client.force_authenticate(user=visualizador)
    return api_client


@pytest.fixture
def no_role_client(api_client, db):
    """Usuario autenticado SIN rol (debe recibir 403 en endpoints RBAC)."""
    user = User.objects.create_user(username='norole', password='pass123')
    api_client.force_authenticate(user=user)
    return api_client
