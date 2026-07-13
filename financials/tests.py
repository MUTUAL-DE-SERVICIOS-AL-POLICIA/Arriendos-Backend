import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from financials.models import Payment, Warranty_Movement, Event_Damage
from leases.models import State, Rental, Selected_Product, Event_Type
from customers.models import Customer, Customer_type
from plans.models import Plan
from rooms.models import Property, Room
from products.models import Product, Rate, HourRange, Price
from decimal import Decimal


def _create_rental():
    ct = Customer_type.objects.create(name='Publico')
    customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
    state = State.objects.create(name='Pre-reserva', next_state=[])
    plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
    return Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)


@pytest.mark.django_db
class TestFinancialModels:
    def test_payment_creation(self):
        ct = Customer_type.objects.create(name='Publico')
        customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)
        payment = Payment.objects.create(
            voucher_number='VCH-001', business_name='Test Corp', nit='1234567',
            detail='Payment for services', payable_mount=5000, amount_paid=5000, rental=rental
        )
        assert payment.voucher_number == 'VCH-001'
        assert 'VCH-001' in str(payment)
        assert 'Test Corp' in str(payment)

    def test_warranty_movement_creation(self):
        ct = Customer_type.objects.create(name='Publico')
        customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)
        warranty = Warranty_Movement.objects.create(
            voucher_number='WRN-001', income=1000, discount=0, returned=0,
            balance=1000, detail='Warranty deposit', rental=rental
        )
        assert warranty.voucher_number == 'WRN-001'
        assert 'WRN-001' in str(warranty)
        assert '1000' in str(warranty)

    def test_event_damage_creation(self):
        rental = _create_rental()
        prop = Property.objects.create(name='Hotel', address='St', department='LP')
        room = Room.objects.create(name='Room1', capacity=50, warranty=500, property=prop, group='A')
        rate = Rate.objects.create(name='Regular')
        hr = HourRange.objects.create(time=4)
        product = Product.objects.create(day=['LUNES'], rate=rate, room=room, hour_range=hr)
        et = Event_Type.objects.create(name='Conferencia')
        sp = Selected_Product.objects.create(
            product=product, rental=rental, event_type=et,
            product_price=500
        )
        wm = Warranty_Movement.objects.create(
            voucher_number='W001', income=Decimal('500'), discount=Decimal('0'),
            returned=Decimal('0'), balance=Decimal('500'), rental=rental
        )
        ed = Event_Damage.objects.create(selected_product=sp, warranty_movement=wm, mount=Decimal('100'))
        assert ed.mount == Decimal('100')
        assert '100' in str(ed)


@pytest.mark.django_db
class TestFinancialAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.rental = _create_rental()

    def test_register_warranty_requires_valid_data(self):
        response = self.client.post('/api/financials/register_warranty/', {}, format='json')
        assert response.status_code == 400

    def test_warranty_requires_valid_data(self):
        response = self.client.post('/api/financials/register_warranty/', {}, format='json')
        assert response.status_code == 400

    def test_discount_warranty_requires_valid_data(self):
        response = self.client.post('/api/financials/discount_warranty/', {}, format='json')
        assert response.status_code == 400

    def test_warranty_returned_requires_valid_data(self):
        response = self.client.post('/api/financials/warranty_returned/', {}, format='json')
        assert response.status_code == 400

    def test_warranty_request_requires_rental(self):
        response = self.client.get('/api/financials/warranty_request/')
        assert response.status_code in [400, 404]

    def test_edit_payment_not_found(self):
        response = self.client.patch('/api/financials/edit_payment/9999/', {}, format='json')
        assert response.status_code in [404, 400]

    def test_edit_warranty_not_found(self):
        response = self.client.patch('/api/financials/edit_warranty/9999/', {}, format='json')
        assert response.status_code in [404, 400]

    def test_register_payment_empty_list(self):
        response = self.client.get(f'/api/financials/register_payment/?rental={self.rental.id}')
        assert response.status_code == 200

    def test_register_payment_with_payments(self):
        Payment.objects.create(
            voucher_number='VCH-001', business_name='Test', nit='1234567',
            detail='Payment', payable_mount=5000, amount_paid=2500, rental=self.rental
        )
        response = self.client.get(f'/api/financials/register_payment/?rental={self.rental.id}')
        assert response.status_code == 200

    def test_register_payment_missing_rental_param(self):
        response = self.client.get('/api/financials/register_payment/')
        assert response.status_code == 400

    def test_register_warranty_empty_list(self):
        response = self.client.get(f'/api/financials/register_warranty/?rental={self.rental.id}')
        assert response.status_code == 200

    def test_register_warranty_with_movements(self):
        Warranty_Movement.objects.create(
            voucher_number='WRN-001', income=1000, discount=0,
            returned=0, balance=1000, rental=self.rental
        )
        response = self.client.get(f'/api/financials/register_warranty/?rental={self.rental.id}')
        assert response.status_code == 200

    def test_register_warranty_missing_rental_param(self):
        response = self.client.get('/api/financials/register_warranty/')
        assert response.status_code == 400