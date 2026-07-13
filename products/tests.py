import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from products.models import Product, Rate, HourRange, Price
from rooms.models import Property, Room


@pytest.mark.django_db
class TestProductModels:
    def test_rate_creation(self):
        rate = Rate.objects.create(name='Regular')
        assert rate.name == 'Regular'
        assert str(rate) == 'Regular'

    def test_hour_range_creation(self):
        hr = HourRange.objects.create(time=4)
        assert hr.time == 4
        assert str(hr) == '4h'

    def test_product_creation(self):
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop)
        rate = Rate.objects.create(name='Regular')
        hr = HourRange.objects.create(time=4)
        product = Product.objects.create(
            day=['LUNES', 'MARTES'],
            rate=rate,
            room=room,
            hour_range=hr
        )
        assert product.day == ['LUNES', 'MARTES']
        assert product.is_deleted is False
        s = str(product)
        assert 'Room1' in s
        assert 'Regular' in s
        assert '4h' in s

    def test_price_creation(self):
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop)
        rate = Rate.objects.create(name='Regular')
        hr = HourRange.objects.create(time=4)
        product = Product.objects.create(day=['LUNES'], rate=rate, room=room, hour_range=hr)
        price = Price.objects.create(mount=500, product=product, is_active=True)
        assert price.mount == 500
        assert price.is_active is True
        s = str(price)
        assert 'Room1' in s
        assert '500' in s
        assert 'vigente' in s

    def test_product_soft_delete(self):
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop)
        rate = Rate.objects.create(name='Regular')
        hr = HourRange.objects.create(time=4)
        product = Product.objects.create(day=['LUNES'], rate=rate, room=room, hour_range=hr)
        product.is_deleted = True
        product.save()
        assert Product.objects.filter(is_deleted=True).count() == 1
        assert Product.objects.filter(is_deleted=False).count() == 0


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

    def test_product_list(self):
        Product.objects.create(day=['LUNES'], rate=self.rate, room=self.room, hour_range=self.hr)
        response = self.client.get('/api/product/')
        assert response.status_code == 200

    def test_rate_list(self):
        Rate.objects.create(name='Regular')
        Rate.objects.create(name='Preferencial')
        response = self.client.get('/api/product/rates/')
        assert response.status_code == 200

    def test_hour_range_list(self):
        HourRange.objects.create(time=4)
        HourRange.objects.create(time=8)
        response = self.client.get('/api/product/hour-range/')
        assert response.status_code == 200

    def test_price_list(self):
        product = Product.objects.create(day=['LUNES'], rate=self.rate, room=self.room, hour_range=self.hr)
        Price.objects.create(mount=500, product=product, is_active=True)
        response = self.client.get('/api/product/price/')
        assert response.status_code == 200

    def test_product_filter_options(self):
        response = self.client.get('/api/product/product_filter_options/')
        assert response.status_code == 200