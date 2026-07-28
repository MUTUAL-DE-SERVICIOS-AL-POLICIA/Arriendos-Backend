"""
Tests de comportamiento para records/utils.py y records/views.py

Comportamientos críticos cubiertos:
- create_record: crea registro con usuario válido
- create_record: user=None no crea registro (silencioso)
- create_record: excepciones se manejan silenciosamente
- available_by_rental: documentos disponibles según estado
- available_by_rental: anulados excluidos

¿Qué debo romper para que estos tests fallen?
- Quitar el guard de None en create_record
- Quitar el try/except en create_record
- Cambiar la lógica de documentos disponibles por estado
"""

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from customers.models import Customer, Customer_type, Contact
from rooms.models import Property, Room
from products.models import Product, Rate, HourRange
from leases.models import State, Rental, Selected_Product, Event_Type
from plans.models import Plan
from financials.models import Payment, Warranty_Movement
from users.models import Record
from records.utils import create_record
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


# ==========================================
# TESTS DE create_record (unit tests)
# ==========================================

@pytest.mark.django_db
class TestCreateRecord:
    """Tests unitarios para la función create_record."""

    def test_creates_record_with_valid_user(self):
        """create_record crea un Record cuando user es válido."""
        user = User.objects.create_user(username='test', password='pass123')
        initial_count = Record.objects.count()

        create_record(user, 'create', 'TestModel', 'Test detail', 1)

        assert Record.objects.count() == initial_count + 1
        record = Record.objects.latest('id')
        assert record.user == user
        assert record.action == 'create'
        assert record.model == 'TestModel'
        assert record.detail == 'Test detail'
        assert record.instance_id == 1

    def test_none_user_does_not_create_record(self):
        """create_record con user=None NO crea registro (retorna silenciosamente)."""
        initial_count = Record.objects.count()

        create_record(None, 'create', 'TestModel', 'Detail', 1)

        assert Record.objects.count() == initial_count

    def test_exception_does_not_propagate(self):
        """create_record maneja excepciones sin propagarlas."""
        user = User.objects.create_user(username='test', password='pass123')

        # No debería lanzar excepción aunque falla internamente
        try:
            create_record(user, 'create', 'TestModel', 'Detail', 99999)
        except Exception:
            pytest.fail("create_record no debería propagar excepciones")


# ==========================================
# TESTS DE available_by_rental (API tests)
# ==========================================

@pytest.mark.django_db
class TestAvailableByRental:
    """Tests del endpoint available_by_rental."""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='pass123')
        self.client.force_authenticate(user=self.user)
        self.s1, self.s2, self.s3, self.s4, self.s5 = _create_states()
        self.customer, self.plan, self.prop, self.room, self.rate, self.hr, self.product, self.et = _create_base()

    def test_anulado_rental_excluded(self):
        """Arriendos anulados (state=5) no aparecen en la lista."""
        Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s5, plan=self.plan)

        response = self.client.get('/api/records/available_by_rental/')

        assert response.status_code == 200
        assert response.data['rentals'] == []

    def test_prereserva_shows_reserva_document(self):
        """Pre-reserva muestra documento de reserva disponible."""
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s1, plan=self.plan)

        response = self.client.get('/api/records/available_by_rental/')

        assert response.status_code == 200
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'reserva' in doc_types

    def test_alquilado_shows_warranty_request_and_return(self):
        """Alquilado muestra documentos de solicitud y devolución de garantía."""
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s3, plan=self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500')
        )

        response = self.client.get('/api/records/available_by_rental/')

        assert response.status_code == 200
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'warranty_request' in doc_types
        assert 'warranty_return' in doc_types

    def test_concluded_hides_warranty_request_and_return(self):
        """Concluido oculta documentos de solicitud/devolución de garantía."""
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s4, plan=self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W001', income=Decimal('500'),
            discount=Decimal('0'), returned=Decimal('0'), balance=Decimal('500')
        )

        response = self.client.get('/api/records/available_by_rental/')

        assert response.status_code == 200
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'warranty_request' not in doc_types
        assert 'warranty_return' not in doc_types

    def test_no_warranty_balance_no_warranty_docs(self):
        """Sin saldo de garantía, no se muestran docs de garantía."""
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s3, plan=self.plan)
        Warranty_Movement.objects.create(
            rental=rental, voucher_number='W001', income=Decimal('500'),
            discount=Decimal('500'), returned=Decimal('0'), balance=Decimal('0')
        )

        response = self.client.get('/api/records/available_by_rental/')

        assert response.status_code == 200
        doc_types = [d['type'] for d in response.data['rentals'][0]['available_documents']]
        assert 'warranty_request' not in doc_types
        assert 'warranty_return' not in doc_types

    def test_customer_institution_name_used(self):
        """Se usa institution_name del customer como nombre principal."""
        rental = Rental.objects.create(initial_total=5000, customer=self.customer, state=self.s1, plan=self.plan)

        response = self.client.get('/api/records/available_by_rental/')

        assert response.data['rentals'][0]['customer_name'] == 'Test Institution'

    def test_customer_without_institution_uses_contact_name(self):
        """Sin institution_name, se usa el nombre del contacto."""
        ct = Customer_type.objects.create(name='Personal')
        customer2 = Customer.objects.create(institution_name=None, nit='9999999', customer_type=ct)
        Contact.objects.create(customer=customer2, name='Maria Lopez', ci_nit='7777', phone='6666666', is_customer=True)
        rental = Rental.objects.create(initial_total=3000, customer=customer2, state=self.s1, plan=self.plan)

        response = self.client.get('/api/records/available_by_rental/')

        assert response.data['rentals'][0]['customer_name'] == 'Maria Lopez'
