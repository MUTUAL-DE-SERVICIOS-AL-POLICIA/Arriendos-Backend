"""
Tests de comportamiento para users/views.py

Comportamientos críticos cubiertos:
- Restricciones de Operador vs Admin en desactivación de usuarios
- No poder desactivar a uno mismo
- No poder desactivar superusers
- No poder desactivar el último administrador
- Toggle de activación/desactivación

¿Qué debo romper para que estos tests fallen?
- Cambiar los guard clauses en User_Delete.delete()
- Cambiar la lógica de UserRole.name == 'Operador'
- Quitar la validación de último administrador
"""

import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from roles.models import Module, Permission, Role, RolePermission, UserRole


def _grant_users_delete_permission(role):
    """Otorga permiso users.delete a un rol para que pase RBAC."""
    module, _ = Module.objects.get_or_create(
        codename='users', defaults={'name': 'Usuarios'}
    )
    perm, _ = Permission.objects.get_or_create(
        codename='delete', defaults={'name': 'Eliminar'}
    )
    rp, _ = RolePermission.objects.get_or_create(role=role, module=module)
    rp.permissions.add(perm)


@pytest.mark.django_db
class TestUserDeactivation:
    """Tests que verifican las restricciones al desactivar usuarios."""

    def setup_method(self):
        self.client = APIClient()

    def test_operator_cannot_deactivate_admin(self):
        """Un Operador con permiso recibe 403 al intentar desactivar un Administrador."""
        admin_role = Role.objects.create(name='Administrador')
        operador_role = Role.objects.create(name='Operador')
        _grant_users_delete_permission(operador_role)

        operador = User.objects.create_user(username='operador1', password='pass123')
        admin = User.objects.create_user(username='admin1', password='pass123')
        UserRole.objects.create(user=operador, role=operador_role)
        UserRole.objects.create(user=admin, role=admin_role)

        self.client.force_authenticate(user=operador)
        response = self.client.delete(f'/api/users/state/{admin.id}')

        assert response.status_code == 403
        assert 'administrador' in response.data['message'].lower()
        admin.refresh_from_db()
        assert admin.is_active is True

    def test_admin_can_deactivate_another_admin(self):
        """Un Administrador con permiso SÍ puede desactivar a otro Administrador."""
        admin_role = Role.objects.create(name='Administrador')
        _grant_users_delete_permission(admin_role)

        admin1 = User.objects.create_user(username='admin1', password='pass123')
        admin2 = User.objects.create_user(username='admin2', password='pass123')
        UserRole.objects.create(user=admin1, role=admin_role)
        UserRole.objects.create(user=admin2, role=admin_role)

        self.client.force_authenticate(user=admin1)
        response = self.client.delete(f'/api/users/state/{admin2.id}')

        assert response.status_code == 200
        admin2.refresh_from_db()
        assert admin2.is_active is False

    def test_cannot_deactivate_self(self):
        """Un usuario no puede desactivar su propia cuenta."""
        role = Role.objects.create(name='Operador')
        _grant_users_delete_permission(role)
        user = User.objects.create_user(username='selfuser', password='pass123')
        UserRole.objects.create(user=user, role=role)
        self.client.force_authenticate(user=user)

        response = self.client.delete(f'/api/users/state/{user.id}')

        assert response.status_code == 400
        assert 'propia cuenta' in response.data['message'].lower()
        user.refresh_from_db()
        assert user.is_active is True

    def test_cannot_deactivate_superuser(self):
        """No se puede desactivar un superuser."""
        admin = User.objects.create_superuser(username='superadmin', password='pass123')
        role = Role.objects.create(name='Operador')
        _grant_users_delete_permission(role)
        other = User.objects.create_user(username='other', password='pass123')
        UserRole.objects.create(user=other, role=role)
        self.client.force_authenticate(user=other)

        response = self.client.delete(f'/api/users/state/{admin.id}')

        assert response.status_code == 400
        assert 'administrador' in response.data['message'].lower()
        admin.refresh_from_db()
        assert admin.is_active is True

    def test_cannot_deactivate_last_admin(self):
        """No se puede desactivar el último Administrador del sistema."""
        admin_role = Role.objects.create(name='Administrador')
        visualizador_role = Role.objects.create(name='Visualizador')
        _grant_users_delete_permission(visualizador_role)

        admin = User.objects.create_user(username='lastadmin', password='pass123')
        visualizador = User.objects.create_user(username='visualizador1', password='pass123')
        UserRole.objects.create(user=admin, role=admin_role)
        UserRole.objects.create(user=visualizador, role=visualizador_role)

        self.client.force_authenticate(user=visualizador)
        response = self.client.delete(f'/api/users/state/{admin.id}')

        assert response.status_code == 400
        admin.refresh_from_db()
        assert admin.is_active is True

    def test_operator_cannot_activate_admin(self):
        """Un Operador con permiso NO puede activar un Administrador (misma restricción que desactivar)."""
        admin_role = Role.objects.create(name='Administrador')
        operador_role = Role.objects.create(name='Operador')
        _grant_users_delete_permission(operador_role)

        operador = User.objects.create_user(username='operador1', password='pass123')
        admin = User.objects.create_user(username='admin1', password='pass123', is_active=False)
        UserRole.objects.create(user=operador, role=operador_role)
        UserRole.objects.create(user=admin, role=admin_role)

        self.client.force_authenticate(user=operador)
        response = self.client.delete(f'/api/users/state/{admin.id}')

        assert response.status_code == 403
        assert 'administrador' in response.data['message'].lower()
        admin.refresh_from_db()
        assert admin.is_active is False

    def test_admin_can_activate_another_admin(self):
        """Un Administrador con permiso SÍ puede activar a otro Administrador."""
        admin_role = Role.objects.create(name='Administrador')
        _grant_users_delete_permission(admin_role)

        admin1 = User.objects.create_user(username='admin1', password='pass123')
        admin2 = User.objects.create_user(username='admin2', password='pass123', is_active=False)
        UserRole.objects.create(user=admin1, role=admin_role)
        UserRole.objects.create(user=admin2, role=admin_role)

        self.client.force_authenticate(user=admin1)
        response = self.client.delete(f'/api/users/state/{admin2.id}')

        assert response.status_code == 200
        admin2.refresh_from_db()
        assert admin2.is_active is True


@pytest.mark.django_db
class TestUserDeactivationEdgeCases:
    """Tests de casos borde en desactivación."""

    def setup_method(self):
        self.client = APIClient()

    def test_deactivate_nonexistent_user_returns_404(self):
        """Desactivar un usuario inexistente retorna 404."""
        role = Role.objects.create(name='Operador')
        _grant_users_delete_permission(role)
        user = User.objects.create_user(username='test', password='pass123')
        UserRole.objects.create(user=user, role=role)
        self.client.force_authenticate(user=user)

        response = self.client.delete('/api/users/state/99999')

        assert response.status_code == 404

    def test_toggle_activation_works_bidirectional(self):
        """El toggle funciona en ambas direcciones: activo→inactivo y viceversa."""
        user = User.objects.create_user(username='toggle', password='pass123')
        admin = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=admin)

        # Desactivar
        response = self.client.delete(f'/api/users/state/{user.id}')
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.is_active is False

        # Reactivar
        response = self.client.delete(f'/api/users/state/{user.id}')
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.is_active is True

    def test_operator_can_deactivate_non_admin_user(self):
        """Un Operador con permiso SÍ puede desactivar usuarios que no son Administrador."""
        operador_role = Role.objects.create(name='Operador')
        visualizador_role = Role.objects.create(name='Visualizador')
        _grant_users_delete_permission(operador_role)

        operador = User.objects.create_user(username='operador1', password='pass123')
        visualizador = User.objects.create_user(username='visualizador1', password='pass123')
        UserRole.objects.create(user=operador, role=operador_role)
        UserRole.objects.create(user=visualizador, role=visualizador_role)

        self.client.force_authenticate(user=operador)
        response = self.client.delete(f'/api/users/state/{visualizador.id}')

        assert response.status_code == 200
        visualizador.refresh_from_db()
        assert visualizador.is_active is False


@pytest.mark.django_db
class TestUserRoleAssignment:
    """Tests de asignación de roles."""

    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=self.admin)

    def test_assign_role_creates_user_role(self):
        """Asignar un rol crea el registro UserRole."""
        role = Role.objects.create(name='Operador')
        user = User.objects.create_user(username='newuser', password='pass123')

        response = self.client.post('/api/roles/assign/', {
            'user_id': user.id, 'role_id': role.id
        }, format='json')

        assert response.status_code == 201
        assert UserRole.objects.filter(user=user, role=role).exists()

    def test_assign_role_replaces_existing(self):
        """Asignar un nuevo rol reemplaza el anterior."""
        role1 = Role.objects.create(name='Operador')
        role2 = Role.objects.create(name='Visualizador')
        user = User.objects.create_user(username='multirole', password='pass123')

        self.client.post('/api/roles/assign/', {
            'user_id': user.id, 'role_id': role1.id
        }, format='json')

        response = self.client.post('/api/roles/assign/', {
            'user_id': user.id, 'role_id': role2.id
        }, format='json')

        assert response.status_code == 201
        assert UserRole.objects.filter(user=user, role=role2).exists()
        assert not UserRole.objects.filter(user=user, role=role1).exists()


@pytest.mark.django_db
class TestUserSearch:
    """Tests de búsqueda de usuarios."""

    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=self.admin)

    def test_search_by_name_returns_matching_users(self):
        """La búsqueda por nombre retorna solo usuarios que coinciden."""
        User.objects.create_user(username='juan1', password='pass123', first_name='Juan')
        User.objects.create_user(username='pedro1', password='pass123', first_name='Pedro')
        User.objects.create_user(username='juan2', password='pass123', first_name='Juan Carlos')

        response = self.client.get('/api/users/?search=Juan')

        assert response.status_code == 200
        assert response.data['total'] == 2
        names = [u['first_name'] for u in response.data['users']]
        assert all('Juan' in n for n in names)

    def test_search_no_results_returns_empty(self):
        """Búsqueda sin resultados retorna lista vacía."""
        User.objects.create_user(username='juan', password='pass123', first_name='Juan')

        response = self.client.get('/api/users/?search=inexistente')

        assert response.status_code == 200
        assert response.data['total'] == 0
        assert response.data['users'] == []
