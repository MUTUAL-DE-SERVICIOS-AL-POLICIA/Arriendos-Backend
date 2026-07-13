import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from users.models import Record


@pytest.mark.django_db
class TestRecordModels:
    def test_record_creation(self):
        user = User.objects.create_user(username='testuser', password='test123')
        record = Record.objects.create(
            action='create',
            model='Product',
            detail='Producto creado: Room1-Regular-4Horas',
            instance_id=1,
            user=user
        )
        assert record.action == 'create'
        assert record.model == 'Product'
        assert 'Room1-Regular-4Horas' in record.detail
        assert record.user == user

    def test_record_str(self):
        user = User.objects.create_user(username='testuser', password='test123')
        record = Record.objects.create(
            action='update',
            model='Rental',
            detail='Alquiler actualizado',
            instance_id=1,
            user=user
        )
        s = str(record)
        assert s is not None
        assert s.startswith('Record object (')


@pytest.mark.django_db
class TestRecordAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_record_list(self):
        Record.objects.create(action='create', model='Product', detail='Test', instance_id=1, user=self.user)
        response = self.client.get('/api/records/')
        assert response.status_code == 200

    def test_record_filter_by_action(self):
        Record.objects.create(action='create', model='Product', detail='Test1', instance_id=1, user=self.user)
        Record.objects.create(action='update', model='Rental', detail='Test2', instance_id=2, user=self.user)
        response = self.client.get('/api/records/?action=create')
        assert response.status_code == 200

    def test_record_filter_by_model(self):
        Record.objects.create(action='create', model='Product', detail='Test', instance_id=1, user=self.user)
        response = self.client.get('/api/records/?model=Product')
        assert response.status_code == 200