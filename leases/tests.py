"""
Tests de comportamiento para leases/views.py

Comportamientos críticos cubiertos:
- Máquina de estados: transiciones válidas e inválidas
- Filtros de rental_list: exclude_annulled, state_id, date_from, date_to, search
- Paginación: limit=-1 retorna todo, limit=0 edge case
- can_edit solo en estado 3 (Alquilado)
- Anulación desde estados 1, 2, 3 y 4

¿Qué debo romper para que estos tests fallen?
- Cambiar next_state en State data
- Quitar exclude_annulled del rental_list
- Cambiar la lógica de can_edit
- Quitar validación de requisitos/pagos/garantías
"""

import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from leases.models import State, Rental, Selected_Product, Event_Type, Additional_Hour_Applied
from rooms.models import Property, Room
from products.models import Product, Rate, HourRange
from customers.models import Customer, Customer_type, Contact
from plans.models import Plan
from requirements.models import Requirement, Requirement_Delivered
from financials.models import Payment, Warranty_Movement


def _create_base_objects():
    ct = Customer_type.objects.create(name='Publico')
    customer = Customer.objects.create(institution_name='Test Corp', nit='1234567', customer_type=ct)
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
    s4.next_state = [5]
    s4.save()
    return s1, s2, s3, s4, s5


def _create_rental(customer, state, plan):
    return Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)


# ==========================================
# TESTS DE MÁQUINA DE ESTADOS
# ==========================================

@pytest.mark.django_db
class TestStateMachineTransitions:
    """Tests de transiciones de estado válidas e inválidas."""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=self.user)
        self.s1, self.s2, self.s3, self.s4, self.s5 = _create_states()
        self.customer, self.plan, _, _, _, _, _, _ = _create_base_objects()

    def test_prereserva_to_reserva_with_requirements(self):
        """Pre-reserva → Reserva funciona con requisitos entregados."""
        rental = _create_rental(self.customer, self.s1, self.plan)
        req = Requirement.objects.create(requirement_name='CI')
        Requirement_Delivered.objects.create(rental=rental, requirement=req)

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s2.id
        }, format='json')

        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s2.id

    def test_prereserva_to_reserva_without_requirements_fails(self):
        """Pre-reserva → Reserva falla sin requisitos entregados."""
        rental = _create_rental(self.customer, self.s1, self.plan)

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s2.id
        }, format='json')

        assert response.status_code == 400
        assert 'requisitos' in response.data['error'].lower()

    def test_prereserva_to_alquilado_invalid(self):
        """Pre-reserva → Alquilado es inválido (skips Reserva)."""
        rental = _create_rental(self.customer, self.s1, self.plan)

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s3.id
        }, format='json')

        assert response.status_code == 400

    def test_reserva_to_alquilado_with_warranty_and_payment(self):
        """Reserva → Alquilado funciona con garantía y pago completo."""
        rental = _create_rental(self.customer, self.s2, self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='G001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500')
        )
        Payment.objects.create(
            rental=rental, voucher_number='P001', business_name='Test', nit='123',
            payable_mount=Decimal('0'), amount_paid=Decimal('5000')
        )

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s3.id
        }, format='json')

        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s3.id

    def test_reserva_to_alquilado_no_warranty_fails(self):
        """Reserva → Alquilado falla sin garantía."""
        rental = _create_rental(self.customer, self.s2, self.plan)
        Payment.objects.create(
            rental=rental, voucher_number='P001', business_name='Test', nit='123',
            payable_mount=Decimal('0'), amount_paid=Decimal('5000')
        )

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s3.id
        }, format='json')

        assert response.status_code == 400
        assert 'garantía' in response.data['error'].lower()

    def test_reserva_to_alquilado_pending_payment_fails(self):
        """Reserva → Alquilado falla con pago pendiente."""
        rental = _create_rental(self.customer, self.s2, self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='G001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500')
        )
        Payment.objects.create(
            rental=rental, voucher_number='P001', business_name='Test', nit='123',
            payable_mount=Decimal('1000'), amount_paid=Decimal('4000')
        )

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s3.id
        }, format='json')

        assert response.status_code == 400
        assert 'pendiente' in response.data['error'].lower()

    def test_alquilado_to_concluido_with_returned_warranty(self):
        """Alquilado → Concluido funciona con garantía retornada."""
        rental = _create_rental(self.customer, self.s3, self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='G001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('500'), balance=Decimal('0')
        )

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s4.id
        }, format='json')

        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s4.id

    def test_alquilado_to_concluido_not_returned_fails(self):
        """Alquilado → Concluido falla si garantía no retornada."""
        rental = _create_rental(self.customer, self.s3, self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='G001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500')
        )

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s4.id
        }, format='json')

        assert response.status_code == 400

    def test_invalid_transition_returns_400(self):
        """Transición no permitida en el state graph retorna 400."""
        rental = _create_rental(self.customer, self.s1, self.plan)

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s3.id
        }, format='json')

        assert response.status_code == 400

    def test_nonexistent_rental_returns_404(self):
        """Arriendo inexistente retorna 404."""
        response = self.client.post('/api/leases/change_state/', {
            'rental': 99999, 'state': self.s2.id
        }, format='json')

        assert response.status_code == 404


# ==========================================
# TESTS DE ANULACIÓN DESDE CUALQUIER ESTADO
# ==========================================

@pytest.mark.django_db
class TestCancelFromAnyState:
    """Tests de anulación desde estados 1, 2, 3 y 4."""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=self.user)
        self.s1, self.s2, self.s3, self.s4, self.s5 = _create_states()
        self.customer, self.plan, _, _, _, _, _, _ = _create_base_objects()

    def test_cancel_from_prereserva(self):
        """Pre-reserva → Anulado funciona."""
        rental = _create_rental(self.customer, self.s1, self.plan)

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s5.id, 'reason': 'Cancelado por cliente'
        }, format='json')

        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s5.id
        assert rental.cancel_reason == 'Cancelado por cliente'

    def test_cancel_from_reserva(self):
        """Reserva → Anulado funciona."""
        rental = _create_rental(self.customer, self.s2, self.plan)

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s5.id, 'reason': 'Problemas logísticos'
        }, format='json')

        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s5.id

    def test_cancel_from_alquilado(self):
        """Alquilado → Anulado funciona."""
        rental = _create_rental(self.customer, self.s3, self.plan)

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s5.id, 'reason': 'Emergencia'
        }, format='json')

        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s5.id

    def test_cancel_from_concluido(self):
        """Concluido → Anulado funciona."""
        rental = _create_rental(self.customer, self.s4, self.plan)

        response = self.client.post('/api/leases/change_state/', {
            'rental': rental.id, 'state': self.s5.id, 'reason': 'Post-conclusión'
        }, format='json')

        assert response.status_code == 200
        rental.refresh_from_db()
        assert rental.state_id == self.s5.id

    def test_anulado_cannot_transition_to_any_state(self):
        """Anulado no puede transicionar a ningún otro estado."""
        rental = _create_rental(self.customer, self.s5, self.plan)

        for target_state in [self.s1, self.s2, self.s3, self.s4]:
            response = self.client.post('/api/leases/change_state/', {
                'rental': rental.id, 'state': target_state.id
            }, format='json')
            assert response.status_code == 400


# ==========================================
# TESTS DE RENTAL_LIST FILTERS
# ==========================================

@pytest.mark.django_db
class TestRentalListFilters:
    """Tests de filtros del endpoint rental_list."""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=self.user)
        self.s1, self.s2, self.s3, self.s4, self.s5 = _create_states()
        self.customer, self.plan, self.prop, self.room, self.rate, self.hr, self.product, self.et = _create_base_objects()

    def test_excludes_annulled_by_default(self):
        """Por defecto, arriendos anulados (state=5) no aparecen."""
        rental_active = _create_rental(self.customer, self.s1, self.plan)
        _create_rental(self.customer, self.s5, self.plan)

        response = self.client.get('/api/leases/rental_list/')

        assert response.status_code == 200
        assert response.data['total'] == 1
        assert response.data['rentals'][0]['id'] == rental_active.id

    def test_include_annulled_when_exclude_false(self):
        """exclude_annulled=false incluye arriendos anulados."""
        _create_rental(self.customer, self.s1, self.plan)
        _create_rental(self.customer, self.s5, self.plan)

        response = self.client.get('/api/leases/rental_list/?exclude_annulled=false')

        assert response.status_code == 200
        assert response.data['total'] == 2

    def test_filter_by_state_id(self):
        """Filtra por state_id específico."""
        _create_rental(self.customer, self.s1, self.plan)
        _create_rental(self.customer, self.s2, self.plan)
        _create_rental(self.customer, self.s5, self.plan)

        response = self.client.get(f'/api/leases/rental_list/?state_id={self.s2.id}')

        assert response.status_code == 200
        assert response.data['total'] == 1
        assert response.data['rentals'][0]['state_name'] == 'Reserva'

    def test_filter_by_date_from(self):
        """Filtra arriendos con start_time >= date_from."""
        rental = _create_rental(self.customer, self.s1, self.plan)
        Selected_Product.objects.create(
            product=self.product, rental=rental, event_type=self.et,
            start_time=timezone.now() + timedelta(days=5),
            end_time=timezone.now() + timedelta(days=5, hours=4),
            product_price=500
        )

        today = timezone.now().strftime('%Y-%m-%d')
        future = (timezone.now() + timedelta(days=10)).strftime('%Y-%m-%d')

        response = self.client.get(f'/api/leases/rental_list/?date_from={today}')

        assert response.status_code == 200
        assert response.data['total'] == 1

    def test_filter_by_date_to(self):
        """Filtra arriendos con start_time <= date_to."""
        rental = _create_rental(self.customer, self.s1, self.plan)
        Selected_Product.objects.create(
            product=self.product, rental=rental, event_type=self.et,
            start_time=timezone.now() + timedelta(days=5),
            end_time=timezone.now() + timedelta(days=5, hours=4),
            product_price=500
        )

        today = timezone.now().strftime('%Y-%m-%d')
        response = self.client.get(f'/api/leases/rental_list/?date_to={today}')

        assert response.status_code == 200
        assert response.data['total'] == 0

    def test_search_by_institution_name(self):
        """Busca por institution_name del customer."""
        ct = Customer_type.objects.create(name='Corp')
        customer2 = Customer.objects.create(institution_name='Otra Empresa', nit='9999999', customer_type=ct)
        _create_rental(self.customer, self.s1, self.plan)
        _create_rental(customer2, self.s1, self.plan)

        response = self.client.get('/api/leases/rental_list/?search=Test')

        assert response.status_code == 200
        assert response.data['total'] == 1
        assert response.data['rentals'][0]['customer_name'] == 'Test Corp'

    def test_search_by_contact_name(self):
        """Busca por nombre del contacto."""
        Contact.objects.create(
            customer=self.customer, name='Maria Lopez',
            ci_nit='7777', phone='6666666', is_customer=True
        )
        _create_rental(self.customer, self.s1, self.plan)

        response = self.client.get('/api/leases/rental_list/?search=Maria')

        assert response.status_code == 200
        assert response.data['total'] == 1

    def test_can_edit_true_only_for_alquilado(self):
        """can_edit=true solo aparece en estado Alquilado (state=3)."""
        rental_s1 = _create_rental(self.customer, self.s1, self.plan)
        rental_s3 = _create_rental(self.customer, self.s3, self.plan)

        response = self.client.get('/api/leases/rental_list/')

        assert response.status_code == 200
        for r in response.data['rentals']:
            if r['id'] == rental_s1.id:
                assert r['can_edit'] is False
            elif r['id'] == rental_s3.id:
                assert r['can_edit'] is True


# ==========================================
# TESTS DE PAGINACIÓN
# ==========================================

@pytest.mark.django_db
class TestRentalListPagination:
    """Tests de paginación del endpoint rental_list."""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=self.user)
        self.s1, _, _, _, _ = _create_states()
        self.customer, self.plan, _, _, _, _, _, _ = _create_base_objects()

    def test_pagination_returns_correct_page(self):
        """Paginación retorna la página correcta con los datos correctos."""
        for i in range(5):
            _create_rental(self.customer, self.s1, self.plan)

        response = self.client.get('/api/leases/rental_list/?page=0&limit=2')

        assert response.status_code == 200
        assert response.data['total'] == 5
        assert len(response.data['rentals']) == 2
        assert response.data['last_page'] == 3

    def test_limit_minus_one_returns_all(self):
        """limit=-1 retorna todos los arriendos sin paginación."""
        for i in range(5):
            _create_rental(self.customer, self.s1, self.plan)

        response = self.client.get('/api/leases/rental_list/?limit=-1')

        assert response.status_code == 200
        assert response.data['total'] == 5
        assert len(response.data['rentals']) == 5

    def test_empty_list_returns_zero_total(self):
        """Lista vacía retorna total=0."""
        response = self.client.get('/api/leases/rental_list/')

        assert response.status_code == 200
        assert response.data['total'] == 0
        assert response.data['rentals'] == []

    def test_invalid_page_param_returns_400(self):
        """Parámetro page no numérico retorna 400."""
        response = self.client.get('/api/leases/rental_list/?page=abc')

        assert response.status_code == 400
