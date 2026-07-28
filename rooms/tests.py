import pytest
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rooms.models import Property, Room, Sub_Room


def _make_photo():
    img = Image.new('RGB', (1, 1), color='red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile('test.jpg', buf.read(), content_type='image/jpeg')


def _make_property(**kwargs):
    defaults = {'name': 'Hotel', 'address': 'St', 'department': 'LP', 'photo': _make_photo()}
    defaults.update(kwargs)
    return Property.objects.create(**defaults)


def _make_room(prop=None, **kwargs):
    if prop is None:
        prop = _make_property()
    defaults = {'name': 'Room1', 'capacity': 50, 'warranty': 500, 'property': prop, 'group': 'A'}
    defaults.update(kwargs)
    return Room.objects.create(**defaults)


# ─────────────────────────────────────────────
# Property CRUD
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestPropertyCRUD:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_property(self):
        prop = _make_property()
        response = self.client.get(f'/api/rooms/properties/{prop.id}/')
        assert response.status_code == 200
        assert response.data['name'] == 'Hotel'

    def test_update_property_name(self):
        prop = _make_property()
        response = self.client.patch(f'/api/rooms/properties/{prop.id}/', {'name': 'Updated'}, format='json')
        assert response.status_code == 200
        prop.refresh_from_db()
        assert prop.name == 'Updated'

    def test_delete_property(self):
        prop = _make_property()
        response = self.client.delete(f'/api/rooms/properties/{prop.id}/')
        assert response.status_code == 204
        assert Property.objects.count() == 0

    def test_retrieve_nonexistent_returns_404(self):
        response = self.client.get('/api/rooms/properties/99999/')
        assert response.status_code == 404

    def test_property_ordered_by_id(self):
        p3 = _make_property(name='Third')
        p1 = _make_property(name='First')
        p2 = _make_property(name='Second')
        response = self.client.get('/api/rooms/properties/')
        assert response.status_code == 200
        ids = [p['id'] for p in response.data['results']] if 'results' in response.data else [p['id'] for p in response.data]
        assert ids == sorted(ids)


# ─────────────────────────────────────────────
# Room CRUD
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRoomCRUD:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_room(self):
        room = _make_room()
        response = self.client.get(f'/api/rooms/{room.id}/')
        assert response.status_code == 200
        assert response.data['name'] == 'Room1'

    def test_update_room_capacity(self):
        room = _make_room()
        response = self.client.patch(f'/api/rooms/{room.id}/', {'capacity': 100}, format='json')
        assert response.status_code == 200
        room.refresh_from_db()
        assert room.capacity == 100

    def test_delete_room(self):
        room = _make_room()
        response = self.client.delete(f'/api/rooms/{room.id}/')
        assert response.status_code == 204
        assert Room.objects.count() == 0

    def test_retrieve_nonexistent_returns_404(self):
        response = self.client.get('/api/rooms/99999/')
        assert response.status_code == 404

    def test_room_filter_by_property(self):
        prop = _make_property(name='Target')
        other_prop = _make_property(name='Other')
        _make_room(prop=prop, name='TargetRoom')
        _make_room(prop=other_prop, name='OtherRoom')
        response = self.client.get(f'/api/rooms/?property_id={prop.id}')
        assert response.status_code == 200


# ─────────────────────────────────────────────
# Sub_Room CRUD
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestSubRoomCRUD:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_update_sub_room_quantity(self):
        prop = _make_property()
        room = _make_room(prop=prop)
        sub = Sub_Room.objects.create(name='Sub1', quantity=5, room=room, state='BUENO')
        response = self.client.patch(f'/api/rooms/sub_rooms/{sub.id}', {'quantity': 20}, format='json')
        assert response.status_code == 200
        sub.refresh_from_db()
        assert sub.quantity == 20

    def test_update_sub_room_state(self):
        prop = _make_property()
        room = _make_room(prop=prop)
        sub = Sub_Room.objects.create(name='Sub1', quantity=5, room=room, state='BUENO')
        response = self.client.patch(f'/api/rooms/sub_rooms/{sub.id}', {'state': 'MALO'}, format='json')
        assert response.status_code == 200
        sub.refresh_from_db()
        assert sub.state == 'MALO'

    def test_update_sub_room_is_active(self):
        prop = _make_property()
        room = _make_room(prop=prop)
        sub = Sub_Room.objects.create(name='Sub1', quantity=5, room=room, state='BUENO', is_active=True)
        response = self.client.patch(f'/api/rooms/sub_rooms/{sub.id}', {'is_active': False}, format='json')
        assert response.status_code == 200
        sub.refresh_from_db()
        assert sub.is_active is False

    def test_create_sub_room_invalid_data_returns_400(self):
        prop = _make_property()
        room = _make_room(prop=prop)
        response = self.client.post('/api/rooms/sub_rooms/', {'name': '', 'room': room.id}, format='json')
        assert response.status_code == 400

    def test_create_sub_room_invalid_state_returns_400(self):
        prop = _make_property()
        room = _make_room(prop=prop)
        response = self.client.post('/api/rooms/sub_rooms/', {
            'name': 'SubX', 'room': room.id, 'quantity': 1, 'state': 'INVALIDO'
        }, format='json')
        assert response.status_code == 400


# ─────────────────────────────────────────────
# List_Properties_with_Rooms
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestPropertiesWithRooms:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_list_properties_with_rooms_endpoint(self):
        prop = _make_property(name='HotelTest')
        room = _make_room(prop=prop)
        Sub_Room.objects.create(name='Sub1', quantity=5, room=room, state='BUENO')
        response = self.client.get('/api/rooms/properties/roomslist/')
        assert response.status_code == 200
        assert 'properties' in response.data
        assert len(response.data['properties']) >= 1

    def test_list_properties_empty(self):
        response = self.client.get('/api/rooms/properties/roomslist/')
        assert response.status_code == 200
        assert 'properties' in response.data
        assert len(response.data['properties']) == 0
