import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from requirements.models import Requirement, RateRequirement, Requirement_Delivered
from products.models import Rate
from customers.models import Customer_type
from leases.models import State, Rental, Selected_Product, Event_Type
from rooms.models import Property, Room
from products.models import Product, HourRange
from plans.models import Plan
from customers.models import Customer
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


def _make_rental_with_rate(state_id=3):
    _create_states()
    ct_customer = Customer_type.objects.create(name='Publico', is_institution=False)
    customer = Customer.objects.create(customer_type=ct_customer)
    plan = Plan.objects.create(plan_name='PlanX', plan_discount=10, rooms_min=1, rooms_max=100)
    rental = Rental.objects.create(initial_total=5000, customer=customer, state_id=state_id, plan=plan)
    prop = Property.objects.create(name='H', address='S', department='LP')
    room = Room.objects.create(name='R', capacity=10, warranty=500, property=prop, group='A')
    rate = Rate.objects.create(name='TarifaBase')
    hr = HourRange.objects.create(time=4)
    product = Product.objects.create(day=['LUNES'], rate=rate, room=room, hour_range=hr)
    et = Event_Type.objects.create(name='Conv')
    now = timezone.now()
    Selected_Product.objects.create(
        product=product, rental=rental, event_type=et, product_price=500,
        start_time=now, end_time=now + timedelta(hours=4)
    )
    return rental, rate, ct_customer


# ─────────────────────────────────────────────
# Requirement CRUD
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRequirementCreate:
    """POST /api/requirements/"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_create_requirement_success(self):
        data = {'requirement_name': 'Fotocopia CI', 'is_active': True}
        response = self.client.post('/api/requirements/', data, format='json')
        assert response.status_code == 201
        assert Requirement.objects.count() == 1
        assert Requirement.objects.first().requirement_name == 'Fotocopia CI'

    def test_create_requirement_missing_name_returns_400(self):
        response = self.client.post('/api/requirements/', {'is_active': True}, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestRequirementPatch:
    """PATCH /api/requirements/<pk>/"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_patch_requirement_success(self):
        req = Requirement.objects.create(requirement_name='Old')
        response = self.client.patch(f'/api/requirements/{req.id}', {'requirement_name': 'New'}, format='json')
        assert response.status_code == 200
        req.refresh_from_db()
        assert req.requirement_name == 'New'

    def test_patch_nonexistent_requirement_returns_404(self):
        response = self.client.patch('/api/requirements/99999', {'requirement_name': 'X'}, format='json')
        assert response.status_code == 404


@pytest.mark.django_db
class TestRequirementToggleDelete:
    """DELETE /api/requirements/<pk>/ — toggle is_active"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_deactivate_requirement(self):
        req = Requirement.objects.create(requirement_name='Test', is_active=True)
        response = self.client.delete(f'/api/requirements/{req.id}')
        assert response.status_code == 200
        req.refresh_from_db()
        assert req.is_active is False

    def test_reactivate_requirement(self):
        req = Requirement.objects.create(requirement_name='Test', is_active=False)
        response = self.client.delete(f'/api/requirements/{req.id}')
        assert response.status_code == 200
        req.refresh_from_db()
        assert req.is_active is True

    def test_toggle_nonexistent_returns_404(self):
        response = self.client.delete('/api/requirements/99999')
        assert response.status_code == 404


# ─────────────────────────────────────────────
# RateRequirement CRUD — URL: /api/requirements/rates/
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRateRequirementCreate:
    """POST /api/requirements/rates/"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_create_rate_requirement_success(self):
        req = Requirement.objects.create(requirement_name='CI')
        ct = Customer_type.objects.create(name='Publico')
        data = {
            'rate': 'Tarifa Nueva',
            'requirement': [req.id],
            'customer_type': [ct.id],
        }
        response = self.client.post('/api/requirements/rates/', data, format='json')
        assert response.status_code == 201
        assert Rate.objects.filter(name='Tarifa Nueva').exists()
        assert RateRequirement.objects.count() == 1

    def test_create_duplicate_rate_name_returns_400(self):
        Rate.objects.create(name='Existente')
        req = Requirement.objects.create(requirement_name='CI')
        ct = Customer_type.objects.create(name='Publico')
        data = {'rate': 'Existente', 'requirement': [req.id], 'customer_type': [ct.id]}
        response = self.client.post('/api/requirements/rates/', data, format='json')
        assert response.status_code == 400
        assert 'existe' in response.data['error'].lower()

    def test_create_rate_requirement_missing_fields_returns_400(self):
        response = self.client.post('/api/requirements/rates/', {}, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestRateRequirementDetail:
    """GET/PATCH /api/requirements/rates/<pk>/"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_get_rate_requirement_success(self):
        rate = Rate.objects.create(name='R1')
        req = Requirement.objects.create(requirement_name='CI')
        ct = Customer_type.objects.create(name='P')
        rr = RateRequirement.objects.create(requirement=req, rate=rate, customer_type=ct)
        response = self.client.get(f'/api/requirements/rates/{rr.id}')
        assert response.status_code == 200

    def test_get_nonexistent_returns_404(self):
        response = self.client.get('/api/requirements/rates/99999')
        assert response.status_code == 404

    def test_patch_rate_requirement_success(self):
        rate = Rate.objects.create(name='OldName')
        req1 = Requirement.objects.create(requirement_name='CI')
        req2 = Requirement.objects.create(requirement_name='Certificado')
        ct = Customer_type.objects.create(name='P')
        RateRequirement.objects.create(requirement=req1, rate=rate, customer_type=ct)
        data = {'name': 'NewName', 'customer_type': [ct.id], 'requirement': [req1.id, req2.id]}
        response = self.client.patch(f'/api/requirements/rates/{rate.id}', data, format='json')
        assert response.status_code == 200
        rate.refresh_from_db()
        assert rate.name == 'NewName'

    def test_patch_rate_requirement_no_customer_type_returns_400(self):
        rate = Rate.objects.create(name='R1')
        response = self.client.patch(
            f'/api/requirements/rates/{rate.id}',
            {'name': 'X', 'customer_type': [], 'requirement': []},
            format='json'
        )
        assert response.status_code == 400


# ─────────────────────────────────────────────
# Requirements_customer — URL: /api/requirements/customer/
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRequirementsCustomer:
    """GET /api/requirements/customer/?rental=X"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_requirements_customer_success(self):
        rental, rate, ct = _make_rental_with_rate()
        req1 = Requirement.objects.create(requirement_name='CI')
        req2 = Requirement.objects.create(requirement_name='Certificado')
        RateRequirement.objects.create(requirement=req1, rate=rate, customer_type=ct)
        response = self.client.get(f'/api/requirements/customer/?rental={rental.id}')
        assert response.status_code == 200
        assert 'required_requirements' in response.data['data']
        assert 'optional_requirements' in response.data['data']
        required = response.data['data']['required_requirements']
        optional = response.data['data']['optional_requirements']
        assert len(required) == 1
        assert required[0]['name'] == 'CI'
        assert len(optional) == 1
        assert optional[0]['name'] == 'Certificado'

    def test_requirements_customer_missing_rental_returns_400(self):
        response = self.client.get('/api/requirements/customer/')
        assert response.status_code == 400

    def test_requirements_customer_no_selected_product_returns_404(self):
        _create_states()
        ct_customer = Customer_type.objects.create(name='P')
        customer = Customer.objects.create(customer_type=ct_customer)
        plan = Plan.objects.create(plan_name='P', plan_discount=0, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=1000, customer=customer, state_id=3, plan=plan)
        response = self.client.get(f'/api/requirements/customer/?rental={rental.id}')
        assert response.status_code == 404

    def test_requirements_customer_no_rate_requirements_returns_404(self):
        rental, rate, ct = _make_rental_with_rate()
        response = self.client.get(f'/api/requirements/customer/?rental={rental.id}')
        assert response.status_code == 404


# ─────────────────────────────────────────────
# RateWithRelatedDataView — URL: /api/requirements/allrates/
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRateWithRelatedData:
    """GET /api/requirements/allrates/"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_list_rates_empty(self):
        response = self.client.get('/api/requirements/allrates/')
        assert response.status_code == 200
        assert response.data['total'] == 0

    def test_list_rates_with_data(self):
        rate = Rate.objects.create(name='R1')
        req = Requirement.objects.create(requirement_name='CI')
        ct = Customer_type.objects.create(name='P')
        RateRequirement.objects.create(requirement=req, rate=rate, customer_type=ct)
        response = self.client.get('/api/requirements/allrates/')
        assert response.status_code == 200
        assert response.data['total'] == 1

    def test_list_rates_pagination(self):
        for i in range(15):
            Rate.objects.create(name=f'R{i}')
        response = self.client.get('/api/requirements/allrates/?page=0&limit=5')
        assert response.status_code == 200
        assert len(response.data['rates']) == 5


# ─────────────────────────────────────────────
# Requirement API list/search
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRequirementList:
    """GET /api/requirements/"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_list_only_active_requirements(self):
        Requirement.objects.create(requirement_name='Active', is_active=True)
        Requirement.objects.create(requirement_name='Inactive', is_active=False)
        response = self.client.get('/api/requirements/')
        assert response.status_code == 200
        assert response.data['total'] == 1
        assert response.data['requirements'][0]['requirement_name'] == 'Active'

    def test_list_with_search(self):
        Requirement.objects.create(requirement_name='Fotocopia CI')
        Requirement.objects.create(requirement_name='Certificado')
        response = self.client.get('/api/requirements/?search=fotocopia')
        assert response.status_code == 200
        assert response.data['total'] == 1
