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
class TestRoomAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

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

    def test_sub_room_update(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        sub = Sub_Room.objects.create(name='Sub1', quantity=5, room=room, state='Disponible')
        response = self.client.patch(f'/api/rooms/sub_rooms/{sub.id}', {'quantity': 20}, format='json')
        assert response.status_code == 200
        sub.refresh_from_db()
        assert sub.quantity == 20

    def test_sub_room_invalid_data(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        data = {'name': '', 'room': room.id}
        response = self.client.post('/api/rooms/sub_rooms/', data, format='json')
        assert response.status_code == 400

    def test_properties_with_rooms_endpoint(self):
        prop = Property.objects.create(name='Hotel', address='St', department='LP', photo=_make_photo())
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        Sub_Room.objects.create(name='Sub1', quantity=5, room=room, state='Disponible')
        response = self.client.get('/api/rooms/properties/roomslist/')
        assert response.status_code == 200
        assert 'properties' in response.data
