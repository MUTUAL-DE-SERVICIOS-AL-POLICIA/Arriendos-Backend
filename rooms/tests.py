import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rooms.models import Property, Room, Sub_Room
import io
from PIL import Image


def _make_photo():
    img = Image.new('RGB', (1, 1), color='red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile('test.jpg', buf.read(), content_type='image/jpeg')


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
        assert 'Hotel' in str(room)

    def test_sub_room_creation(self):
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        room = Room.objects.create(name='Salón 1', capacity=50, warranty=500, property=prop)
        sub = Sub_Room.objects.create(name='Sub1', quantity=5, room=room, state='Disponible')
        assert sub.quantity == 5
        assert 'Sub1' in str(sub)
        assert 'Salón 1' in str(sub)

    def test_property_str(self):
        prop = Property.objects.create(name='Test Hotel', address='Av. 1', department='CBBA')
        assert str(prop) == 'Test Hotel'

    def test_room_str(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP')
        room = Room.objects.create(name='Room A', capacity=10, warranty=100, property=prop, group='VIP')
        assert 'Room A' in str(room)
        assert 'Hotel' in str(room)

    def test_sub_room_str(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP')
        room = Room.objects.create(name='Room', capacity=10, warranty=100, property=prop, group='A')
        sub = Sub_Room.objects.create(name='Sub A', quantity=3, room=room, state='Activo')
        assert 'Sub A' in str(sub)
        assert 'Room' in str(sub)

    def test_room_is_active_default(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP')
        room = Room.objects.create(name='R1', capacity=10, warranty=100, property=prop, group='A')
        assert room.is_active is True


@pytest.mark.django_db
class TestRoomAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_property_list(self):
        Property.objects.create(name='Hotel', address='Main St', department='LP', photo=_make_photo())
        response = self.client.get('/api/rooms/properties/')
        assert response.status_code == 200

    def test_property_create(self):
        data = {'name': 'Nuevo Hotel', 'address': 'Av. 1', 'department': 'CBBA', 'photo': _make_photo()}
        response = self.client.post('/api/rooms/properties/', data)
        assert response.status_code == 201

    def test_property_retrieve(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        response = self.client.get(f'/api/rooms/properties/{prop.id}/')
        assert response.status_code == 200
        assert response.data['name'] == 'Hotel'

    def test_property_update(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        response = self.client.patch(f'/api/rooms/properties/{prop.id}/', {'name': 'Hotel Updated'}, format='json')
        assert response.status_code == 200
        prop.refresh_from_db()
        assert prop.name == 'Hotel Updated'

    def test_property_delete(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        response = self.client.delete(f'/api/rooms/properties/{prop.id}/')
        assert response.status_code == 204
        assert Property.objects.count() == 0

    def test_room_list(self):
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP', photo=_make_photo())
        Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        response = self.client.get('/api/rooms/')
        assert response.status_code == 200

    def test_room_create(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        data = {'name': 'New Room', 'capacity': 30, 'warranty': 300, 'property': prop.id, 'group': 'B'}
        response = self.client.post('/api/rooms/', data, format='json')
        assert response.status_code == 201

    def test_room_retrieve(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        response = self.client.get(f'/api/rooms/{room.id}/')
        assert response.status_code == 200
        assert response.data['name'] == 'Room1'

    def test_room_update(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        response = self.client.patch(f'/api/rooms/{room.id}/', {'capacity': 100}, format='json')
        assert response.status_code == 200
        room.refresh_from_db()
        assert room.capacity == 100

    def test_room_delete(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        response = self.client.delete(f'/api/rooms/{room.id}/')
        assert response.status_code == 204
        assert Room.objects.count() == 0

    def test_room_filter_by_property(self):
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP', photo=_make_photo())
        Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        response = self.client.get(f'/api/rooms/?property_id={prop.id}')
        assert response.status_code == 200

    def test_room_no_filter(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        Room.objects.create(name='R1', capacity=10, warranty=100, property=prop, group='A')
        response = self.client.get('/api/rooms/')
        assert response.status_code == 200

    def test_property_not_found(self):
        response = self.client.get('/api/rooms/properties/9999/')
        assert response.status_code == 404

    def test_room_not_found(self):
        response = self.client.get('/api/rooms/9999/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestSubRoomAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        self.room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')

    def test_sub_room_list(self):
        Sub_Room.objects.create(name='Sub1', quantity=5, room=self.room, state='Disponible')
        response = self.client.get('/api/rooms/sub_rooms/')
        assert response.status_code == 200
        assert response.data['total'] == 1

    def test_sub_room_create(self):
        data = {'name': 'New Sub', 'quantity': 10, 'room': self.room.id, 'state': 'Activo'}
        response = self.client.post('/api/rooms/sub_rooms/', data, format='json')
        assert response.status_code == 201

    def test_sub_room_retrieve(self):
        sub = Sub_Room.objects.create(name='Sub1', quantity=5, room=self.room, state='Disponible')
        response = self.client.get(f'/api/rooms/sub_rooms/{sub.id}')
        assert response.status_code == 200

    def test_sub_room_update(self):
        sub = Sub_Room.objects.create(name='Sub1', quantity=5, room=self.room, state='Disponible')
        response = self.client.patch(f'/api/rooms/sub_rooms/{sub.id}', {'quantity': 20}, format='json')
        assert response.status_code == 200
        sub.refresh_from_db()
        assert sub.quantity == 20

    def test_sub_room_not_found(self):
        response = self.client.get('/api/rooms/sub_rooms/9999')
        assert response.status_code == 404

    def test_sub_room_invalid_data(self):
        data = {'name': '', 'room': self.room.id}
        response = self.client.post('/api/rooms/sub_rooms/', data, format='json')
        assert response.status_code == 400

    def test_properties_with_rooms_endpoint(self):
        Sub_Room.objects.create(name='Sub1', quantity=5, room=self.room, state='Disponible')
        response = self.client.get('/api/rooms/properties/roomslist/')
        assert response.status_code == 200
        assert 'properties' in response.data