import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from products.models import Product, Rate, HourRange, Price
from rooms.models import Property, Room


@pytest.mark.django_db
class TestProductAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        self.room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=self.prop)
        self.rate = Rate.objects.create(name='Regular')
        self.hr = HourRange.objects.create(time=4)

    def test_product_create_with_price(self):
        data = {
            'day': ['LUNES', 'MARTES'],
            'rate': self.rate.id,
            'room': self.room.id,
            'hour_range': self.hr.id,
            'mount': 750
        }
        response = self.client.post('/api/product/', data, format='json')
        assert response.status_code == 201
        assert response.data['status'] == 'success'
        product_data = response.data['data'][0]
        price_data = response.data['data'][1]
        assert product_data['id'] is not None
        assert price_data['mount'] == 750
        assert price_data['is_active'] is True
        assert Price.objects.filter(product_id=product_data['id'], is_active=True).exists()

    def test_product_create_invalid_price_deletes_product(self):
        data = {
            'day': ['LUNES'],
            'rate': self.rate.id,
            'room': self.room.id,
            'hour_range': self.hr.id,
            'mount': 'abc'
        }
        initial_count = Product.objects.count()
        response = self.client.post('/api/product/', data, format='json')
        assert response.status_code == 400
        assert Product.objects.count() == initial_count

    def test_product_list_excludes_deleted(self):
        Product.objects.create(day=['LUNES'], rate=self.rate, room=self.room, hour_range=self.hr)
        deleted = Product.objects.create(day=['MARTES'], rate=self.rate, room=self.room, hour_range=self.hr)
        deleted.is_deleted = True
        deleted.save()
        response = self.client.get('/api/product/')
        assert response.status_code == 200
        assert response.data['total'] == 1

    def test_product_soft_delete_via_api(self):
        product = Product.objects.create(day=['LUNES'], rate=self.rate, room=self.room, hour_range=self.hr)
        response = self.client.delete(f'/api/product/{product.id}')
        assert response.status_code == 200
        product.refresh_from_db()
        assert product.is_deleted is True

    def test_product_patch_with_price(self):
        product = Product.objects.create(day=['LUNES'], rate=self.rate, room=self.room, hour_range=self.hr)
        Price.objects.create(mount=500, product=product, is_active=True)
        response = self.client.patch(f'/api/product/{product.id}', {'mount': 900}, format='json')
        assert response.status_code == 200
        assert response.data['data']['price']['mount'] == 900
        old_price = Price.objects.filter(product=product, is_active=False).first()
        assert old_price is not None
        new_price = Price.objects.filter(product=product, is_active=True).first()
        assert new_price.mount == 900
