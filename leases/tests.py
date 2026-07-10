import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from leases.models import State, Rental, Selected_Product, Event_Type
from rooms.models import Property, Room
from products.models import Product, Rate, HourRange, Price
from customers.models import Customer, Customer_type
from plans.models import Plan


@pytest.mark.django_db
class TestLeaseModels:
    def test_state_creation(self):
        state = State.objects.create(name='Pre-reserva', next_state=[])
        assert state.name == 'Pre-reserva'
        assert str(state) == 'Pre-reserva'

    def test_event_type_creation(self):
        et = Event_Type.objects.create(name='Conferencia')
        assert et.name == 'Conferencia'

    def test_rental_creation(self):
        ct = Customer_type.objects.create(name='Público')
        customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)
        assert rental.initial_total == 5000

    def test_selected_product_creation(self):
        ct = Customer_type.objects.create(name='Público')
        customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop)
        rate = Rate.objects.create(name='Regular')
        hr = HourRange.objects.create(time=4)
        product = Product.objects.create(day=['LUNES'], rate=rate, room=room, hour_range=hr)
        et = Event_Type.objects.create(name='Conferencia')
        now = timezone.now()
        sp = Selected_Product.objects.create(
            start_time=now,
            end_time=now + timedelta(hours=4),
            product_price=500,
            rental=rental,
            product=product,
            event_type=et
        )
        assert sp.product_price == 500


@pytest.mark.django_db
class TestLeaseAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.state = State.objects.create(name='Pre-reserva', next_state=[])

    def test_state_list(self):
        State.objects.create(name='Reserva', next_state=[])
        response = self.client.get('/api/leases/state/')
        assert response.status_code == 200

    def test_rental_filter_options(self):
        response = self.client.get('/api/leases/rental_filter_options/')
        assert response.status_code == 200
        assert 'states' in response.data

    def test_event_type_list(self):
        Event_Type.objects.create(name='Conferencia')
        response = self.client.get('/api/leases/event/')
        assert response.status_code == 200
