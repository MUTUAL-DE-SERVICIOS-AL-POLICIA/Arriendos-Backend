import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rooms.models import Property, Room, Sub_Room


@pytest.mark.django_db
class TestRoomModels:
    def test_property_creation(self):
        prop = Property.objects.create(name='Gran Hotel París', address='Av. Principal', department='La Paz')
        assert prop.name == 'Gran Hotel París'
        assert str(prop) == 'Gran Hotel París'

    def test_room_creation(self):
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        room = Room.objects.create(name='Salón 1', capacity=50, warranty=500, property=prop)
        assert room.name == 'Salón 1'
        assert 'Salón 1' in str(room)

    def test_sub_room_creation(self):
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        room = Room.objects.create(name='Salón 1', capacity=50, warranty=500, property=prop)
        sub = Sub_Room.objects.create(name='Sub1', quantity=5, room=room)
        assert sub.quantity == 5


@pytest.mark.django_db
class TestRoomAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_property_list(self):
        Property.objects.create(name='Hotel', address='Main St', department='LP')
        response = self.client.get('/api/rooms/properties/')
        assert response.status_code == 200

    def test_room_list(self):
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop)
        response = self.client.get('/api/rooms/')
        assert response.status_code == 200

    def test_room_filter_by_property(self):
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop)
        response = self.client.get(f'/api/rooms/?property_id={prop.id}')
        assert response.status_code == 200
