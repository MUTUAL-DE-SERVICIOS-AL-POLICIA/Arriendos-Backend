import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from requirements.models import Requirement, RateRequirement
from products.models import Rate
from customers.models import Customer_type


@pytest.mark.django_db
class TestRequirementAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_requirement_create(self):
        data = {'requirement_name': 'Nuevo requisito', 'is_active': True}
        response = self.client.post('/api/requirements/', data, format='json')
        assert response.status_code == 201
        assert Requirement.objects.count() == 1

    def test_requirement_update(self):
        req = Requirement.objects.create(requirement_name='Test')
        response = self.client.patch(f'/api/requirements/{req.id}', {'requirement_name': 'New'}, format='json')
        assert response.status_code == 200
        req.refresh_from_db()
        assert req.requirement_name == 'New'
