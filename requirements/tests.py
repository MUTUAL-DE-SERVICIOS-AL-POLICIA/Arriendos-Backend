import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from requirements.models import Requirement, RateRequirement
from products.models import Rate
from customers.models import Customer_type


@pytest.mark.django_db
class TestRequirementModels:
    def test_requirement_creation(self):
        req = Requirement.objects.create(requirement_name='CI del arrendatario', is_active=True)
        assert req.requirement_name == 'CI del arrendatario'
        assert req.is_active is True

    def test_rate_requirement_creation(self):
        rate = Rate.objects.create(name='Regular')
        ct = Customer_type.objects.create(name='Público')
        req = Requirement.objects.create(requirement_name='CI')
        rr = RateRequirement.objects.create(rate=rate, requirement=req, customer_type=ct)
        assert rr.rate == rate
        assert rr.requirement == req


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
