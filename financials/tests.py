import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from financials.models import Payment, Warranty_Movement
from leases.models import State, Rental
from customers.models import Customer, Customer_type
from plans.models import Plan


@pytest.mark.django_db
class TestFinancialModels:
    def test_payment_creation(self):
        ct = Customer_type.objects.create(name='Público')
        customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)
        payment = Payment.objects.create(
            voucher_number='VCH-001',
            business_name='Test Corp',
            nit='1234567',
            detail='Payment for services',
            payable_mount=5000,
            amount_paid=5000,
            rental=rental
        )
        assert payment.voucher_number == 'VCH-001'
        assert 'VCH-001' in str(payment)
        assert 'Test Corp' in str(payment)

    def test_warranty_movement_creation(self):
        ct = Customer_type.objects.create(name='Público')
        customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)
        warranty = Warranty_Movement.objects.create(
            voucher_number='WRN-001',
            income=1000,
            discount=0,
            returned=0,
            balance=1000,
            detail='Warranty deposit',
            rental=rental
        )
        assert warranty.voucher_number == 'WRN-001'
        assert 'WRN-001' in str(warranty)
        assert '1000' in str(warranty)