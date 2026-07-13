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
from requirements.models import Requirement, Requirement_Delivered
from financials.models import Payment, Warranty_Movement
from decimal import Decimal


def _create_base_objects():
    ct = Customer_type.objects.create(name='Publico')
    customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
    plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
    prop = Property.objects.create(name='Hotel', address='St', department='LP')
    room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
    rate = Rate.objects.create(name='Regular')
    hr = HourRange.objects.create(time=4)
    product = Product.objects.create(day=['LUNES'], rate=rate, room=room, hour_range=hr)
    et = Event_Type.objects.create(name='Conferencia')
    return customer, plan, prop, room, rate, hr, product, et


def _create_states():
    s1 = State.objects.create(id=1, name='Pre-reserva', next_state=[])
    s2 = State.objects.create(id=2, name='Reserva', next_state=[])
    s3 = State.objects.create(id=3, name='Alquilado', next_state=[])
    s4 = State.objects.create(id=4, name='Concluido', next_state=[])
    s5 = State.objects.create(id=5, name='Anulado', next_state=[])
    s1.next_state = [s2.id, s5.id]
    s1.save()
    s2.next_state = [s3.id, s5.id]
    s2.save()
    s3.next_state = [s4.id, s5.id]
    s3.save()
    return s1, s2, s3, s4, s5


def _create_rental(customer, state, plan):
    return Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)


@pytest.mark.django_db
class TestLeaseModels:
    def test_state_creation(self):
        state = State.objects.create(name='Pre-reserva', next_state=[])
        assert state.name == 'Pre-reserva'
        assert str(state) == 'Pre-reserva'

    def test_event_type_creation(self):
        et = Event_Type.objects.create(name='Conferencia')
        assert et.name == 'Conferencia'
        assert str(et) == 'Conferencia'

    def test_rental_creation(self):
        ct = Customer_type.objects.create(name='Publico')
        customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)
        assert rental.initial_total == 5000
        assert 'Arriendo' in str(rental)

    def test_rental_str_with_contract(self):
        ct = Customer_type.objects.create(name='Publico')
        customer = Customer.objects.create(institution_name='Test', nit='123', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan, contract_number='C001')
        assert 'C001' in str(rental)

    def test_selected_product_creation(self):
        ct = Customer_type.objects.create(name='Publico')
        customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)
        prop = Property.objects.create(name='Hotel', address='Main St', department='LP')
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        rate = Rate.objects.create(name='Regular')
        hr = HourRange.objects.create(time=4)
        product = Product.objects.create(day=['LUNES'], rate=rate, room=room, hour_range=hr)
        et = Event_Type.objects.create(name='Conferencia')
        now = timezone.now()
        sp = Selected_Product.objects.create(
            start_time=now, end_time=now + timedelta(hours=4),
            product_price=500, rental=rental, product=product, event_type=et
        )
        assert sp.product_price == 500
        s = str(sp)
        assert 'Regular' in s
        assert 'Room1' in s
        assert 'Conferencia' in s

    def test_additional_hour_applied_creation(self):
        from leases.models import Additional_Hour_Applied
        ct = Customer_type.objects.create(name='Publico')
        customer = Customer.objects.create(institution_name='Test', nit='123', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)
        prop = Property.objects.create(name='Hotel', address='St', department='LP')
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        rate = Rate.objects.create(name='Regular')
        hr = HourRange.objects.create(time=4)
        product = Product.objects.create(day=['LUNES'], rate=rate, room=room, hour_range=hr)
        et = Event_Type.objects.create(name='Conferencia')
        now = timezone.now()
        sp = Selected_Product.objects.create(
            start_time=now, end_time=now + timedelta(hours=4),
            product_price=500, rental=rental, product=product, event_type=et
        )
        aha = Additional_Hour_Applied.objects.create(
            selected_product=sp, number=1, voucher_number='V001',
            business_name='Test', nit='123', total=200, description='Hora extra'
        )
        assert aha.total == 200
        assert 'Hora extra' in str(aha)


@pytest.mark.django_db
class TestLeaseAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.s1, self.s2, self.s3, self.s4, self.s5 = _create_states()
        self.customer, self.plan, _, _, _, _, _, _ = _create_base_objects()

    def test_state_list(self):
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

    def test_change_state(self):
        rental = _create_rental(self.customer, self.s1, self.plan)
        req = Requirement.objects.create(requirement_name='CI')
        Requirement_Delivered.objects.create(rental=rental, requirement=req)
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s2.id}, format='json')
        assert response.status_code == 200

    def test_change_state_missing_fields(self):
        response = self.client.post('/api/leases/change_state/', {}, format='json')
        assert response.status_code == 400

    def test_change_state_rental_not_found(self):
        response = self.client.post('/api/leases/change_state/', {'rental': 9999, 'state': self.s2.id}, format='json')
        assert response.status_code == 404


@pytest.mark.django_db
class TestStateMachine:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.s1, self.s2, self.s3, self.s4, self.s5 = _create_states()
        self.customer, self.plan, self.prop, self.room, self.rate, self.hr, self.product, self.et = _create_base_objects()

    def test_prereserva_to_reserva(self):
        rental = _create_rental(self.customer, self.s1, self.plan)
        req = Requirement.objects.create(requirement_name='CI')
        Requirement_Delivered.objects.create(rental=rental, requirement=req)
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s2.id}, format='json')
        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s2.id

    def test_prereserva_to_reserva_without_requirements_fails(self):
        rental = _create_rental(self.customer, self.s1, self.plan)
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s2.id}, format='json')
        assert response.status_code == 400

    def test_prereserva_to_anulado(self):
        rental = _create_rental(self.customer, self.s1, self.plan)
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s5.id, 'reason': 'Cancelado'}, format='json')
        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s5.id

    def test_prereserva_to_alquilado_invalid(self):
        rental = _create_rental(self.customer, self.s1, self.plan)
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s3.id}, format='json')
        assert response.status_code == 400

    def test_reserva_to_alquilado(self):
        rental = _create_rental(self.customer, self.s2, self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='G001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500')
        )
        Payment.objects.create(
            rental=rental, voucher_number='P001', business_name='Test', nit='123',
            payable_mount=Decimal('0'), amount_paid=Decimal('5000')
        )
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s3.id}, format='json')
        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s3.id

    def test_reserva_to_alquilado_no_warranty_fails(self):
        rental = _create_rental(self.customer, self.s2, self.plan)
        Payment.objects.create(
            rental=rental, voucher_number='P001', business_name='Test', nit='123',
            payable_mount=Decimal('0'), amount_paid=Decimal('5000')
        )
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s3.id}, format='json')
        assert response.status_code == 400

    def test_reserva_to_alquilado_no_payment_fails(self):
        rental = _create_rental(self.customer, self.s2, self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='G001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500')
        )
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s3.id}, format='json')
        assert response.status_code == 400

    def test_reserva_to_alquilado_pending_payment_fails(self):
        rental = _create_rental(self.customer, self.s2, self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='G001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500')
        )
        Payment.objects.create(
            rental=rental, voucher_number='P001', business_name='Test', nit='123',
            payable_mount=Decimal('1000'), amount_paid=Decimal('4000')
        )
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s3.id}, format='json')
        assert response.status_code == 400

    def test_alquilado_to_concluido(self):
        rental = _create_rental(self.customer, self.s3, self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='G001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('500'), balance=Decimal('0')
        )
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s4.id}, format='json')
        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s4.id

    def test_alquilado_to_concluido_not_returned_fails(self):
        rental = _create_rental(self.customer, self.s3, self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='G001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500')
        )
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s4.id}, format='json')
        assert response.status_code == 400

    def test_reserva_to_anulado(self):
        rental = _create_rental(self.customer, self.s2, self.plan)
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s5.id, 'reason': 'Cancelado'}, format='json')
        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s5.id

    def test_anulado_cannot_transition(self):
        rental = _create_rental(self.customer, self.s5, self.plan)
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s1.id}, format='json')
        assert response.status_code == 400

    def test_concluido_cannot_transition(self):
        rental = _create_rental(self.customer, self.s4, self.plan)
        response = self.client.post('/api/leases/change_state/', {'rental': rental.id, 'state': self.s1.id}, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestRentalListAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.s1, _, _, _, _ = _create_states()
        self.customer, self.plan, _, _, _, _, _, _ = _create_base_objects()

    def test_rental_list_empty(self):
        response = self.client.get('/api/leases/rental_list/')
        assert response.status_code == 200
        assert response.data['total'] == 0

    def test_rental_list_with_data(self):
        _create_rental(self.customer, self.s1, self.plan)
        response = self.client.get('/api/leases/rental_list/')
        assert response.status_code == 200
        assert response.data['total'] == 1

    def test_rental_list_filter_by_state(self):
        _create_rental(self.customer, self.s1, self.plan)
        response = self.client.get(f'/api/leases/rental_list/?state_id={self.s1.id}')
        assert response.status_code == 200
        assert response.data['total'] == 1

    def test_rental_list_filter_by_search(self):
        _create_rental(self.customer, self.s1, self.plan)
        response = self.client.get('/api/leases/rental_list/?search=Test')
        assert response.status_code == 200

    def test_rental_list_limit_all(self):
        _create_rental(self.customer, self.s1, self.plan)
        response = self.client.get('/api/leases/rental_list/?limit=-1')
        assert response.status_code == 200
        assert response.data['total'] == 1