import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from requirements.models import Requirement, RateRequirement, Requirement_Delivered
from products.models import Rate
from customers.models import Customer_type, Customer
from leases.models import State, Rental
from plans.models import Plan


@pytest.mark.django_db
class TestRequirementModels:
    def test_requirement_creation(self):
        req = Requirement.objects.create(requirement_name='CI del arrendatario', is_active=True)
        assert req.requirement_name == 'CI del arrendatario'
        assert req.is_active is True
        assert str(req) == 'CI del arrendatario'

    def test_requirement_inactive(self):
        req = Requirement.objects.create(requirement_name='Test', is_active=False)
        assert req.is_active is False

    def test_rate_requirement_creation(self):
        rate = Rate.objects.create(name='Regular')
        ct = Customer_type.objects.create(name='Publico')
        req = Requirement.objects.create(requirement_name='CI')
        rr = RateRequirement.objects.create(rate=rate, requirement=req, customer_type=ct)
        assert rr.rate == rate
        assert rr.requirement == req
        s = str(rr)
        assert 'CI' in s
        assert 'Regular' in s
        assert 'Publico' in s

    def test_rate_requirement_inactive(self):
        rate = Rate.objects.create(name='Regular')
        ct = Customer_type.objects.create(name='Publico')
        req = Requirement.objects.create(requirement_name='CI')
        rr = RateRequirement.objects.create(rate=rate, requirement=req, customer_type=ct, is_active=False)
        assert rr.is_active is False

    def test_requirement_delivered_creation(self):
        ct = Customer_type.objects.create(name='Publico')
        customer = Customer.objects.create(institution_name='Test', nit='123', customer_type=ct)
        state = State.objects.create(name='Pre-reserva', next_state=[])
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=1, rooms_max=100)
        rental = Rental.objects.create(initial_total=5000, customer=customer, state=state, plan=plan)
        req = Requirement.objects.create(requirement_name='CI')
        rd = Requirement_Delivered.objects.create(rental=rental, requirement=req)
        assert rd.rental == rental
        assert rd.requirement == req
        s = str(rd)
        assert 'CI' in s
        assert 'Arriendo' in s


@pytest.mark.django_db
class TestRequirementAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_requirement_list(self):
        Requirement.objects.create(requirement_name='CI')
        response = self.client.get('/api/requirements/')
        assert response.status_code == 200

    def test_requirement_create(self):
        data = {'requirement_name': 'Nuevo requisito', 'is_active': True}
        response = self.client.post('/api/requirements/', data, format='json')
        assert response.status_code == 201
        assert Requirement.objects.count() == 1

    def test_requirement_create_invalid(self):
        data = {'requirement_name': '', 'is_active': True}
        response = self.client.post('/api/requirements/', data, format='json')
        assert response.status_code in [400, 404]

    def test_requirement_update(self):
        req = Requirement.objects.create(requirement_name='Test')
        response = self.client.patch(f'/api/requirements/{req.id}', {'requirement_name': 'New'}, format='json')
        assert response.status_code == 200
        req.refresh_from_db()
        assert req.requirement_name == 'New'

    def test_rate_requirement_detail(self):
        rate = Rate.objects.create(name='Regular')
        ct = Customer_type.objects.create(name='Publico')
        req = Requirement.objects.create(requirement_name='CI')
        rr = RateRequirement.objects.create(rate=rate, requirement=req, customer_type=ct)
        response = self.client.get(f'/api/requirements/rates/{rr.id}')
        assert response.status_code == 200

    def test_allrates_endpoint(self):
        rate = Rate.objects.create(name='Regular')
        ct = Customer_type.objects.create(name='Publico')
        req = Requirement.objects.create(requirement_name='CI')
        RateRequirement.objects.create(rate=rate, requirement=req, customer_type=ct)
        response = self.client.get('/api/requirements/allrates/')
        assert response.status_code == 200