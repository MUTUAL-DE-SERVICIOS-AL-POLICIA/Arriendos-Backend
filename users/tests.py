import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from users.models import Record, Assign
from rooms.models import Property, Room
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image


def _make_photo():
    img = Image.new('RGB', (1, 1), color='red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile('test.jpg', buf.read(), content_type='image/jpeg')


@pytest.mark.django_db
class TestUserModels:
    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', password='testpass123', email='test@test.com')
        assert user.username == 'testuser'
        assert user.check_password('testpass123')
        assert user.email == 'test@test.com'

    def test_superuser_creation(self):
        user = User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        assert user.username == 'admin'
        assert user.is_superuser is True
        assert user.is_staff is True

    def test_record_model(self):
        user = User.objects.create_user(username='testuser', password='test123')
        record = Record.objects.create(
            action='create',
            model='Product',
            detail='Test record',
            instance_id=1,
            user=user
        )
        assert record.action == 'create'
        assert record.user == user
        assert 'Test record' in record.detail

    def test_record_no_user(self):
        record = Record.objects.create(
            action='create',
            model='Product',
            detail='No user record',
            instance_id=2,
            user=None
        )
        assert record.user is None
        assert record.action == 'create'

    def test_assign_model(self):
        user = User.objects.create_user(username='assignee', password='pass123')
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        room = Room.objects.create(name='Room1', capacity=10, warranty=100, property=prop, group='A')
        assign = Assign.objects.create(user=user, room=room)
        assert assign.user == user
        assert assign.room == room


@pytest.mark.django_db
class TestUserAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        self.client.force_authenticate(user=self.user)

    def test_user_list(self):
        User.objects.create_user(username='user1', password='pass123')
        User.objects.create_user(username='user2', password='pass123')
        response = self.client.get('/api/users/')
        assert response.status_code == 200

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
        from roles.models import Role, UserRole
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

    def test_user_limit_all(self):
        User.objects.create_user(username='u1', password='pass123')
        User.objects.create_user(username='u2', password='pass123')
        response = self.client.get('/api/users/?limit=-1')
        assert response.status_code == 200
        assert response.data['total'] == 3  # admin + u1 + u2


@pytest.mark.django_db
class TestUserDeleteAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        self.client.force_authenticate(user=self.user)

    def test_user_not_found(self):
        response = self.client.delete('/api/users/state/9999')
        assert response.status_code == 404

    def test_cannot_deactivate_self(self):
        response = self.client.delete(f'/api/users/state/{self.user.id}')
        assert response.status_code == 400
        self.user.refresh_from_db()
        assert self.user.is_active is True

    def test_cannot_deactivate_superuser(self):
        superuser = User.objects.create_superuser(username='other_admin', password='pass123')
        response = self.client.delete(f'/api/users/state/{superuser.id}')
        assert response.status_code == 400


@pytest.mark.django_db
class TestAssignAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        self.room = Room.objects.create(name='Room1', capacity=10, warranty=100, property=prop, group='A')
        self.regular_user = User.objects.create_user(username='assignee', password='pass123')

    def test_assign_create(self):
        data = [{'user': self.regular_user.id, 'room': self.room.id}]
        response = self.client.post('/api/users/assign/', data, format='json')
        assert response.status_code == 201

    def test_assign_list(self):
        Assign.objects.create(user=self.regular_user, room=self.room)
        response = self.client.get('/api/users/assign/')
        assert response.status_code == 200

    def test_assign_retrieve(self):
        assign = Assign.objects.create(user=self.regular_user, room=self.room)
        response = self.client.get(f'/api/users/assign/{assign.id}')
        assert response.status_code == 200

    def test_assign_update(self):
        assign = Assign.objects.create(user=self.regular_user, room=self.room)
        new_user = User.objects.create_user(username='newuser', password='pass123')
        response = self.client.patch(f'/api/users/assign/{assign.id}', {'user': new_user.id}, format='json')
        assert response.status_code == 200

    def test_assign_not_found(self):
        response = self.client.get('/api/users/assign/9999')
        assert response.status_code == 404