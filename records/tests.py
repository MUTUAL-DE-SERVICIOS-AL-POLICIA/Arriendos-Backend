import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from customers.models import Customer, Customer_type, Contact
from rooms.models import Property, Room
from products.models import Product, Rate, HourRange
from leases.models import State, Rental, Selected_Product, Event_Type
from plans.models import Plan
from financials.models import Payment, Warranty_Movement
from decimal import Decimal


def _create_base():
    ct = Customer_type.objects.create(name='Publico')
    customer = Customer.objects.create(institution_name='Test Institution', nit='1234567', customer_type=ct)
    Contact.objects.create(customer=customer, name='Juan Perez', ci_nit='8888', phone='7777777', is_customer=True)
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
    return s1, s2, s3, s4, s5


@pytest.mark.django_db
class TestAvailableByRentalApi:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.s1, self.s2, self.s3, self.s4, self.s5 = _create_states()
        self.customer, self.plan, self.prop, self.room, self.rate, self.hr, self.product, self.et = _create_base()

    def test_rental_with_customer_shows_reserva(self):
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s1, plan=self.plan)
        response = self.client.get('/api/records/available_by_rental/')
        assert response.status_code == 200
        assert len(response.data['rentals']) == 1
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'reserva' in doc_types

    def test_rental_with_products_shows_entrega(self):
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s2, plan=self.plan)
        Selected_Product.objects.create(product=self.product, rental=rental, event_type=self.et, product_price=500)
        response = self.client.get('/api/records/available_by_rental/')
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'entrega' in doc_types

    def test_rental_with_payments_shows_payments(self):
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s2, plan=self.plan)
        Payment.objects.create(rental=rental, voucher_number='V001', business_name='Test', nit='123',
                               payable_mount=5000, amount_paid=5000)
        response = self.client.get('/api/records/available_by_rental/')
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'payments' in doc_types

    def test_rental_with_warranties_shows_warranties(self):
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s2, plan=self.plan)
        Warranty_Movement.objects.create(rental=rental, voucher_number='W001', income=Decimal('500'),
                                         discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500'))
        response = self.client.get('/api/records/available_by_rental/')
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'warranties' in doc_types

    def test_concluded_rental_hides_warranty_request_and_return(self):
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s4, plan=self.plan)
        Warranty_Movement.objects.create(rental=rental, voucher_number='W001', income=Decimal('500'),
                                         discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500'))
        response = self.client.get('/api/records/available_by_rental/')
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'warranty_request' not in doc_types
        assert 'warranty_return' not in doc_types
        assert 'warranties' in doc_types

    def test_alquilado_rental_shows_warranty_request_and_return(self):
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s3, plan=self.plan)
        Warranty_Movement.objects.create(rental=rental, voucher_number='W001', income=Decimal('500'),
                                         discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500'))
        response = self.client.get('/api/records/available_by_rental/')
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'warranty_request' in doc_types
        assert 'warranty_return' in doc_types

    def test_anulado_rental_excluded(self):
        Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s5, plan=self.plan)
        response = self.client.get('/api/records/available_by_rental/')
        assert response.data['rentals'] == []

    def test_no_warranty_balance_no_warranty_docs(self):
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s3, plan=self.plan)
        Warranty_Movement.objects.create(rental=rental, voucher_number='W001', income=Decimal('500'),
                                         discount=Decimal('500'), returned=Decimal('0'), balance=Decimal('0'))
        response = self.client.get('/api/records/available_by_rental/')
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'warranty_request' not in doc_types
        assert 'warranty_return' not in doc_types

    def test_customer_institution_name_used(self):
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s1, plan=self.plan)
        response = self.client.get('/api/records/available_by_rental/')
        assert response.data['rentals'][0]['customer_name'] == 'Test Institution'

    def test_customer_without_institution_uses_contact_name(self):
        ct = Customer_type.objects.create(name='Personal')
        customer2 = Customer.objects.create(institution_name=None, nit='9999999', customer_type=ct)
        Contact.objects.create(customer=customer2, name='Maria Lopez', ci_nit='7777', phone='6666666', is_customer=True)
        rental = Rental.objects.create(initial_total=3000, customer=customer2, state=self.s1, plan=self.plan)
        response = self.client.get('/api/records/available_by_rental/')
        assert response.data['rentals'][0]['customer_name'] == 'Maria Lopez'
