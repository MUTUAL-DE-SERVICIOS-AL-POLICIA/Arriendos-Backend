import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from financials.models import Payment, Warranty_Movement
from leases.models import State, Rental, Selected_Product, Event_Type
from customers.models import Customer, Customer_type
from plans.models import Plan
from rooms.models import Property, Room
from products.models import Product, Rate, HourRange
from decimal import Decimal


def _create_states():
    s1 = State.objects.create(id=1, name='Pre-reserva', next_state=[])
    s2 = State.objects.create(id=2, name='Reserva', next_state=[])
    s3 = State.objects.create(id=3, name='Alquilado', next_state=[])
    s4 = State.objects.create(id=4, name='Concluido', next_state=[])
    s5 = State.objects.create(id=5, name='Anulado', next_state=[])
    return s1, s2, s3, s4, s5


def _create_rental_with_state(state_id):
    ct = Customer_type.objects.create(name='Publico')
    customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
    state = State.objects.get(id=state_id)
    plan = Plan.objects.create(plan_name='Plan X', plan_discount=10, rooms_min=1, rooms_max=100)
    return Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)


@pytest.mark.django_db
class TestWarrantyReturnRequest:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        _create_states()

    def test_concluded_rental_returns_404(self):
        rental = _create_rental_with_state(4)
        Warranty_Movement.objects.create(
            voucher_number='WRN-001', income=1000, discount=0,
            returned=0, balance=1000, rental=rental
        )
        response = self.client.get(f'/api/financials/warranty_request/?rental={rental.id}')
        assert response.status_code == 404
        assert 'retornado' in response.data['error'].lower()

    def test_no_warranty_movements(self):
        rental = _create_rental_with_state(3)
        response = self.client.get(f'/api/financials/warranty_request/?rental={rental.id}')
        assert response.status_code == 400


@pytest.mark.django_db
class TestReturnWarrantyForm:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        _create_states()

    def test_concluded_rental_returns_404(self):
        rental = _create_rental_with_state(4)
        Warranty_Movement.objects.create(
            voucher_number='WRN-001', income=1000, discount=0,
            returned=0, balance=1000, rental=rental
        )
        response = self.client.get(f'/api/financials/return_warranty_form/?rental={rental.id}')
        assert response.status_code == 404
        assert 'retornado' in response.data['error'].lower()

    def test_no_warranty_movements(self):
        rental = _create_rental_with_state(3)
        response = self.client.get(f'/api/financials/return_warranty_form/?rental={rental.id}')
        assert response.status_code == 404


@pytest.mark.django_db
class TestDiscountWarrantyConcluded:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        _create_states()

    def test_concluded_rental_returns_400(self):
        rental = _create_rental_with_state(4)
        prop = Property.objects.create(name='H', address='S', department='LP')
        room = Room.objects.create(name='R', capacity=10, warranty=100, property=prop, group='A')
        rate = Rate.objects.create(name='R')
        hr = HourRange.objects.create(time=4)
        product = Product.objects.create(day=['LUNES'], rate=rate, room=room, hour_range=hr)
        et = Event_Type.objects.create(name='Conv')
        sp = Selected_Product.objects.create(product=product, rental=rental, event_type=et, product_price=500)
        Warranty_Movement.objects.create(
            voucher_number='WRN-001', income=1000, discount=0,
            returned=0, balance=1000, rental=rental
        )
        response = self.client.post('/api/financials/discount_warranty/', {
            'rental': rental.id,
            'product': sp.id,
            'detail': 'Daño',
            'discount': 100
        }, format='json')
        assert response.status_code == 400
        assert 'retornado' in response.data['error'].lower()

    def test_discount_zero_returns_400(self):
        rental = _create_rental_with_state(3)
        prop = Property.objects.create(name='H2', address='S2', department='LP')
        room = Room.objects.create(name='R2', capacity=10, warranty=100, property=prop, group='B')
        rate = Rate.objects.create(name='R2')
        hr = HourRange.objects.create(time=2)
        product = Product.objects.create(day=['MARTES'], rate=rate, room=room, hour_range=hr)
        et = Event_Type.objects.create(name='Reu')
        sp = Selected_Product.objects.create(product=product, rental=rental, event_type=et, product_price=300)
        Warranty_Movement.objects.create(
            voucher_number='WRN-002', income=1000, discount=0,
            returned=0, balance=1000, rental=rental
        )
        response = self.client.post('/api/financials/discount_warranty/', {
            'rental': rental.id,
            'product': sp.id,
            'detail': 'Daño',
            'discount': 0
        }, format='json')
        assert response.status_code == 400
