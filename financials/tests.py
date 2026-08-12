import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from financials.models import Payment, Warranty_Movement, Event_Damage
from leases.models import State, Rental, Selected_Product, Event_Type
from customers.models import Customer, Customer_type, Contact
from plans.models import Plan
from rooms.models import Property, Room
from products.models import Product, Rate, HourRange
from django.utils import timezone
from datetime import timedelta


def _create_states():
    for sid, name, nxt in [
        (1, 'Pre-reserva', []),
        (2, 'Reserva', []),
        (3, 'Alquilado', []),
        (4, 'Concluido', []),
        (5, 'Anulado', []),
    ]:
        State.objects.get_or_create(id=sid, defaults={'name': name, 'next_state': nxt})


def _make_rental(state_id, initial_total=5000):
    _create_states()
    ct = Customer_type.objects.create(name='Publico')
    customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
    Contact.objects.create(name='Contact Test', ci_nit='1234567', phone='7777777', customer=customer)
    plan = Plan.objects.create(plan_name='Plan X', plan_discount=10, rooms_min=1, rooms_max=100)
    return Rental.objects.create(initial_total=initial_total, customer=customer, state_id=state_id, plan=plan)


def _make_rental_with_product(state_id, initial_total=5000):
    rental = _make_rental(state_id, initial_total)
    prop = Property.objects.create(name='H', address='S', department='LP')
    room = Room.objects.create(name='R', capacity=10, warranty=500, property=prop, group='A')
    rate = Rate.objects.create(name='TarifaTest')
    hr = HourRange.objects.create(time=4)
    product = Product.objects.create(day=['LUNES'], rate=rate, room=room, hour_range=hr)
    et = Event_Type.objects.create(name='Convencion')
    now = timezone.now()
    sp = Selected_Product.objects.create(
        product=product, rental=rental, event_type=et, product_price=500,
        start_time=now, end_time=now + timedelta(hours=4)
    )
    return rental, sp


# ─────────────────────────────────────────────
# Register_payment tests
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRegisterPaymentPost:
    """POST /api/financials/register_payment/ — registrar pagos"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_register_first_payment_success(self):
        rental = _make_rental(3, initial_total=5000)
        data = {
            'rental': rental.id,
            'detail': 'Pago inicial',
            'mount': 2000,
            'business_name': 'Mi Empresa',
            'nit': '1234567890',
            'voucher_number': 'V-001',
        }
        response = self.client.post('/api/financials/register_payment/', data, format='json')
        assert response.status_code == 201
        assert response.data['state'] == 'success'
        payment = Payment.objects.get(rental=rental)
        assert payment.amount_paid == Decimal('2000')
        assert payment.payable_mount == Decimal('3000')

    def test_register_payment_exceeding_total_returns_400(self):
        rental = _make_rental(3, initial_total=1000)
        data = {
            'rental': rental.id,
            'detail': 'Exceso',
            'mount': 2000,
            'business_name': 'Empresa',
            'nit': '999',
            'voucher_number': 'V-002',
        }
        response = self.client.post('/api/financials/register_payment/', data, format='json')
        assert response.status_code == 400
        assert 'mayor' in response.data['error'].lower()

    def test_register_payment_mount_zero_returns_400(self):
        rental = _make_rental(3)
        data = {
            'rental': rental.id,
            'detail': 'Zero',
            'mount': 0,
            'business_name': 'E',
            'nit': '0',
            'voucher_number': 'V-003',
        }
        response = self.client.post('/api/financials/register_payment/', data, format='json')
        assert response.status_code == 400
        assert 'mayor 0' in response.data['error']

    def test_register_payment_missing_fields_returns_400(self):
        response = self.client.post('/api/financials/register_payment/', {}, format='json')
        assert response.status_code == 400

    def test_register_payment_nonexistent_rental_returns_404(self):
        data = {
            'rental': 99999,
            'detail': 'X',
            'mount': 100,
            'business_name': 'E',
            'nit': '0',
            'voucher_number': 'V-004',
        }
        response = self.client.post('/api/financials/register_payment/', data, format='json')
        assert response.status_code == 404

    def test_register_second_payment_decreases_payable(self):
        rental = _make_rental(3, initial_total=5000)
        self.client.post('/api/financials/register_payment/', {
            'rental': rental.id, 'detail': 'P1', 'mount': 2000,
            'business_name': 'E', 'nit': '0', 'voucher_number': 'V-1',
        }, format='json')
        response = self.client.post('/api/financials/register_payment/', {
            'rental': rental.id, 'detail': 'P2', 'mount': 1500,
            'business_name': 'E', 'nit': '0', 'voucher_number': 'V-2',
        }, format='json')
        assert response.status_code == 201
        last_payment = Payment.objects.filter(rental=rental).latest('id')
        assert last_payment.payable_mount == Decimal('1500')

    def test_register_second_payment_exceeding_balance_returns_400(self):
        rental = _make_rental(3, initial_total=1000)
        self.client.post('/api/financials/register_payment/', {
            'rental': rental.id, 'detail': 'P1', 'mount': 800,
            'business_name': 'E', 'nit': '0', 'voucher_number': 'V-1',
        }, format='json')
        response = self.client.post('/api/financials/register_payment/', {
            'rental': rental.id, 'detail': 'P2', 'mount': 500,
            'business_name': 'E', 'nit': '0', 'voucher_number': 'V-2',
        }, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestRegisterPaymentGet:
    """GET /api/financials/register_payment/?rental=X — listar pagos"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_list_payments_empty(self):
        rental = _make_rental(3)
        response = self.client.get(f'/api/financials/register_payment/?rental={rental.id}')
        assert response.status_code == 200
        assert response.data['payments'] == []
        assert response.data['payable_mount'] == 0

    def test_list_payments_with_data(self):
        rental = _make_rental(3, initial_total=3000)
        Payment.objects.create(rental=rental, voucher_number='V1', business_name='E', nit='0',
                               detail='d', payable_mount=Decimal('1000'), amount_paid=Decimal('2000'))
        response = self.client.get(f'/api/financials/register_payment/?rental={rental.id}')
        assert response.status_code == 200
        assert len(response.data['payments']) == 1
        assert response.data['payable_mount'] == Decimal('1000')

    def test_list_payments_missing_rental_param_returns_400(self):
        response = self.client.get('/api/financials/register_payment/')
        assert response.status_code == 400

    def test_list_payments_nonexistent_rental_returns_404(self):
        response = self.client.get('/api/financials/register_payment/?rental=99999')
        assert response.status_code == 404


@pytest.mark.django_db
class TestRegisterPaymentDelete:
    """DELETE /api/financials/register_payment/<rental_id>/ — eliminar último pago"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_delete_last_payment_success(self):
        rental = _make_rental(3, initial_total=3000)
        Payment.objects.create(rental=rental, voucher_number='V1', business_name='E', nit='0',
                               detail='d', payable_mount=Decimal('1000'), amount_paid=Decimal('2000'))
        assert Payment.objects.filter(rental=rental).count() == 1
        response = self.client.delete(f'/api/financials/register_payment/{rental.id}/')
        assert response.status_code == 200
        assert Payment.objects.filter(rental=rental).count() == 0

    def test_delete_payment_no_payments_returns_400(self):
        rental = _make_rental(3)
        response = self.client.delete(f'/api/financials/register_payment/{rental.id}/')
        assert response.status_code == 400
        assert 'no existen' in response.data['error'].lower()


# ─────────────────────────────────────────────
# Register_warranty tests
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRegisterWarrantyPost:
    """POST /api/financials/register_warranty/ — registrar garantía"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_register_first_warranty_success(self):
        rental = _make_rental(3)
        data = {
            'rental': rental.id,
            'income': 1000,
            'detail': 'Garantía inicial',
            'voucher_number': 'WRN-001',
        }
        response = self.client.post('/api/financials/register_warranty/', data, format='json')
        assert response.status_code == 201
        wm = Warranty_Movement.objects.get(rental=rental)
        assert wm.balance == Decimal('1000')
        assert wm.income == Decimal('1000')
        assert wm.discount == Decimal('0')
        assert wm.returned == Decimal('0')

    def test_register_warranty_income_zero_returns_400(self):
        rental = _make_rental(3)
        data = {'rental': rental.id, 'income': 0, 'detail': 'X', 'voucher_number': 'WRN-002'}
        response = self.client.post('/api/financials/register_warranty/', data, format='json')
        assert response.status_code == 400

    def test_register_warranty_missing_fields_returns_400(self):
        response = self.client.post('/api/financials/register_warranty/', {}, format='json')
        assert response.status_code == 400

    def test_register_warranty_nonexistent_rental_returns_404(self):
        data = {'rental': 99999, 'income': 500, 'detail': 'X', 'voucher_number': 'WRN-003'}
        response = self.client.post('/api/financials/register_warranty/', data, format='json')
        assert response.status_code == 404

    def test_register_second_warranty_accumulates_balance(self):
        rental = _make_rental(3)
        self.client.post('/api/financials/register_warranty/', {
            'rental': rental.id, 'income': 1000, 'detail': 'P1', 'voucher_number': 'W1',
        }, format='json')
        response = self.client.post('/api/financials/register_warranty/', {
            'rental': rental.id, 'income': 500, 'detail': 'P2', 'voucher_number': 'W2',
        }, format='json')
        assert response.status_code == 201
        wm = Warranty_Movement.objects.filter(rental=rental).latest('id')
        assert wm.balance == Decimal('1500')


@pytest.mark.django_db
class TestRegisterWarrantyGet:
    """GET /api/financials/register_warranty/?rental=X — listar garantías"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_list_warranties_empty(self):
        rental = _make_rental(3)
        response = self.client.get(f'/api/financials/register_warranty/?rental={rental.id}')
        assert response.status_code == 200
        assert response.data['warranty_movements'] == []

    def test_list_warranties_with_data(self):
        rental = _make_rental(3)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('1000'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('1000')
        )
        response = self.client.get(f'/api/financials/register_warranty/?rental={rental.id}')
        assert response.status_code == 200
        assert len(response.data['warranty_movements']) == 1

    def test_list_warranties_missing_rental_returns_400(self):
        response = self.client.get('/api/financials/register_warranty/')
        assert response.status_code == 400

    def test_list_warranties_nonexistent_rental_returns_404(self):
        response = self.client.get('/api/financials/register_warranty/?rental=99999')
        assert response.status_code == 404


@pytest.mark.django_db
class TestRegisterWarrantyDelete:
    """DELETE /api/financials/register_warranty/<rental_id>/ — eliminar última garantía"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_delete_last_warranty_success(self):
        rental = _make_rental(3)
        wm = Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('1000'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('1000')
        )
        response = self.client.delete(f'/api/financials/register_warranty/{rental.id}/')
        assert response.status_code == 200
        assert Warranty_Movement.objects.filter(rental=rental).count() == 0

    def test_delete_warranty_cascades_event_damage(self):
        rental, sp = _make_rental_with_product(3)
        wm = Warranty_Movement.objects.create(
            rental=rental, voucher_number='WD', income=Decimal('0'),
            discount=Decimal('100'), returned=Decimal('0'), balance=Decimal('900')
        )
        Event_Damage.objects.create(mount=Decimal('100'), selected_product=sp, warranty_movement=wm)
        assert Event_Damage.objects.count() == 1
        response = self.client.delete(f'/api/financials/register_warranty/{rental.id}/')
        assert response.status_code == 200
        assert Event_Damage.objects.count() == 0

    def test_delete_warranty_no_warranties_returns_400(self):
        rental = _make_rental(3)
        response = self.client.delete(f'/api/financials/register_warranty/{rental.id}/')
        assert response.status_code == 400


# ─────────────────────────────────────────────
# Discount_warranty tests
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestDiscountWarranty:
    """POST /api/financials/discount_warranty/ — descuento por daños"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_discount_success(self):
        rental, sp = _make_rental_with_product(3)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('1000'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('1000')
        )
        data = {'rental': rental.id, 'product': sp.id, 'detail': 'Silla rota', 'discount': 100}
        response = self.client.post('/api/financials/discount_warranty/', data, format='json')
        assert response.status_code == 200
        wm = Warranty_Movement.objects.filter(rental=rental).latest('id')
        assert wm.balance == Decimal('900')
        assert wm.discount == Decimal('100')
        assert Event_Damage.objects.filter(warranty_movement=wm).exists()

    def test_discount_concluded_rental_returns_400(self):
        rental, sp = _make_rental_with_product(4)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('1000'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('1000')
        )
        data = {'rental': rental.id, 'product': sp.id, 'detail': 'Daño', 'discount': 100}
        response = self.client.post('/api/financials/discount_warranty/', data, format='json')
        assert response.status_code == 400
        assert 'retornado' in response.data['error'].lower()

    def test_discount_zero_returns_400(self):
        rental, sp = _make_rental_with_product(3)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('1000'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('1000')
        )
        data = {'rental': rental.id, 'product': sp.id, 'detail': 'Daño', 'discount': 0}
        response = self.client.post('/api/financials/discount_warranty/', data, format='json')
        assert response.status_code == 400

    def test_discount_exceeding_balance_returns_400(self):
        rental, sp = _make_rental_with_product(3)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('100'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('100')
        )
        data = {'rental': rental.id, 'product': sp.id, 'detail': 'Daño grave', 'discount': 500}
        response = self.client.post('/api/financials/discount_warranty/', data, format='json')
        assert response.status_code == 400
        assert 'mayor' in response.data['error'].lower()

    def test_discount_no_warranties_returns_400(self):
        rental, sp = _make_rental_with_product(3)
        data = {'rental': rental.id, 'product': sp.id, 'detail': 'Daño', 'discount': 50}
        response = self.client.post('/api/financials/discount_warranty/', data, format='json')
        assert response.status_code == 400

    def test_discount_nonexistent_rental_returns_404(self):
        data = {'rental': 99999, 'product': 1, 'detail': 'X', 'discount': 50}
        response = self.client.post('/api/financials/discount_warranty/', data, format='json')
        assert response.status_code == 404

    def test_discount_invalid_product_returns_400(self):
        rental = _make_rental(3)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('1000'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('1000')
        )
        data = {'rental': rental.id, 'product': 99999, 'detail': 'X', 'discount': 50}
        response = self.client.post('/api/financials/discount_warranty/', data, format='json')
        assert response.status_code == 400
        assert 'producto' in response.data['error'].lower()


# ─────────────────────────────────────────────
# Warranty_Returned tests
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestWarrantyReturned:
    """POST /api/financials/warranty_returned/ — devolver garantía"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_warranty_returned_success(self):
        rental = _make_rental(3)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('1000'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('1000')
        )
        data = {'rental': rental.id, 'return_date': '2025-01-15T10:30:00.000Z'}
        response = self.client.post('/api/financials/warranty_returned/', data, format='json')
        assert response.status_code == 201
        wm = Warranty_Movement.objects.filter(rental=rental).latest('id')
        assert wm.balance == Decimal('0')
        assert wm.returned == Decimal('1000')
        rental.refresh_from_db()
        assert rental.warranty_returned is not None

    def test_warranty_returned_zero_balance_returns_400(self):
        rental = _make_rental(3)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('0'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('0')
        )
        data = {'rental': rental.id, 'return_date': '2025-01-15T10:30:00.000Z'}
        response = self.client.post('/api/financials/warranty_returned/', data, format='json')
        assert response.status_code == 400

    def test_warranty_returned_no_warranties_returns_400(self):
        rental = _make_rental(3)
        data = {'rental': rental.id, 'return_date': '2025-01-15T10:30:00.000Z'}
        response = self.client.post('/api/financials/warranty_returned/', data, format='json')
        assert response.status_code == 400

    def test_warranty_returned_nonexistent_rental_returns_404(self):
        data = {'rental': 99999, 'return_date': '2025-01-15T10:30:00.000Z'}
        response = self.client.post('/api/financials/warranty_returned/', data, format='json')
        assert response.status_code == 404

    def test_warranty_returned_missing_fields_returns_400(self):
        response = self.client.post('/api/financials/warranty_returned/', {}, format='json')
        assert response.status_code == 400


# ─────────────────────────────────────────────
# Warranty_Return_Request tests
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestWarrantyReturnRequest:
    """GET /api/financials/warranty_request/?rental=X — solicitud devolución"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_concluded_rental_returns_200(self):
        rental = _make_rental_with_product(4)[0]
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('1000'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('1000')
        )
        response = self.client.get(f'/api/financials/warranty_request/?rental={rental.id}')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'

    def test_no_warranty_movements_returns_400(self):
        rental = _make_rental(3)
        response = self.client.get(f'/api/financials/warranty_request/?rental={rental.id}')
        assert response.status_code == 400

    def test_missing_rental_param_returns_404(self):
        response = self.client.get('/api/financials/warranty_request/')
        assert response.status_code == 404


# ─────────────────────────────────────────────
# Return_Warranty_Form tests
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestReturnWarrantyForm:
    """GET /api/financials/return_warranty_form/?rental=X"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_concluded_rental_returns_200(self):
        rental = _make_rental_with_product(4)[0]
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W1', income=Decimal('1000'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('1000')
        )
        response = self.client.get(f'/api/financials/return_warranty_form/?rental={rental.id}')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'

    def test_no_warranty_movements_returns_404(self):
        rental = _make_rental(3)
        response = self.client.get(f'/api/financials/return_warranty_form/?rental={rental.id}')
        assert response.status_code == 404

    def test_missing_rental_param_returns_400(self):
        response = self.client.get('/api/financials/return_warranty_form/')
        assert response.status_code == 400


# ─────────────────────────────────────────────
# Edit_payment tests
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestEditPayment:
    """PATCH /api/financials/edit_payment/<pk>/ — editar pago"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_edit_payment_success(self):
        rental = _make_rental(3, initial_total=5000)
        payment = Payment.objects.create(
            rental=rental, voucher_number='V1', business_name='E', nit='0',
            detail='d', payable_mount=Decimal('3000'), amount_paid=Decimal('2000')
        )
        response = self.client.patch(
            f'/api/financials/edit_payment/{payment.id}/',
            {'amount_paid': 1500}, format='json'
        )
        assert response.status_code == 200
        assert response.data['state'] == 'success'
        payment.refresh_from_db()
        assert payment.amount_paid == Decimal('1500')

    def test_edit_payment_missing_amount_returns_400(self):
        rental = _make_rental(3)
        payment = Payment.objects.create(
            rental=rental, voucher_number='V1', business_name='E', nit='0',
            detail='d', payable_mount=Decimal('3000'), amount_paid=Decimal('2000')
        )
        response = self.client.patch(f'/api/financials/edit_payment/{payment.id}/', {}, format='json')
        assert response.status_code == 400

    def test_edit_payment_non_numeric_amount_returns_400(self):
        rental = _make_rental(3)
        payment = Payment.objects.create(
            rental=rental, voucher_number='V1', business_name='E', nit='0',
            detail='d', payable_mount=Decimal('3000'), amount_paid=Decimal('2000')
        )
        response = self.client.patch(
            f'/api/financials/edit_payment/{payment.id}/',
            {'amount_paid': 'abc'}, format='json'
        )
        assert response.status_code == 400

    def test_edit_payment_exceeding_total_returns_400(self):
        rental = _make_rental(3, initial_total=1000)
        payment = Payment.objects.create(
            rental=rental, voucher_number='V1', business_name='E', nit='0',
            detail='d', payable_mount=Decimal('0'), amount_paid=Decimal('1000')
        )
        response = self.client.patch(
            f'/api/financials/edit_payment/{payment.id}/',
            {'amount_paid': 2000}, format='json'
        )
        assert response.status_code == 400

    def test_edit_nonexistent_payment_returns_404(self):
        response = self.client.patch('/api/financials/edit_payment/99999/', {'amount_paid': 100}, format='json')
        assert response.status_code == 404


@pytest.mark.django_db
class TestEditPaymentGet:
    """GET /api/financials/edit_payment/<pk>/"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_get_payment_success(self):
        rental = _make_rental(3)
        payment = Payment.objects.create(
            rental=rental, voucher_number='V1', business_name='E', nit='0',
            detail='d', payable_mount=Decimal('3000'), amount_paid=Decimal('2000')
        )
        response = self.client.get(f'/api/financials/edit_payment/{payment.id}/')
        assert response.status_code == 200
        assert response.data['voucher_number'] == 'V1'

    def test_get_nonexistent_payment_returns_404(self):
        response = self.client.get('/api/financials/edit_payment/99999/')
        assert response.status_code == 404
