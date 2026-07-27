import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from leases.models import State, Rental, Selected_Product, Event_Type, Additional_Hour_Applied
from rooms.models import Property, Room
from products.models import Product, Rate, HourRange
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
