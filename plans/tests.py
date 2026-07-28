import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from plans.models import Plan


@pytest.mark.django_db
class TestPlanCRUD:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_create_plan_success(self):
        data = {'plan_name': 'Plan Gold', 'plan_discount': 15, 'rooms_min': 1, 'rooms_max': 50}
        response = self.client.post('/api/plans/', data, format='json')
        assert response.status_code == 201
        assert Plan.objects.count() == 1
        assert Plan.objects.first().plan_name == 'Plan Gold'

    def test_create_plan_missing_fields_returns_400(self):
        response = self.client.post('/api/plans/', {}, format='json')
        assert response.status_code == 400

    def test_list_plans(self):
        Plan.objects.create(plan_name='P1', plan_discount=10, rooms_min=1, rooms_max=100)
        Plan.objects.create(plan_name='P2', plan_discount=20, rooms_min=1, rooms_max=100)
        response = self.client.get('/api/plans/')
        assert response.status_code == 200

    def test_create_plan_negative_discount(self):
        data = {'plan_name': 'Bad', 'plan_discount': -5, 'rooms_min': 1, 'rooms_max': 10}
        response = self.client.post('/api/plans/', data, format='json')
        assert response.status_code == 201

    def test_create_plan_zero_discount(self):
        data = {'plan_name': 'Free', 'plan_discount': 0, 'rooms_min': 1, 'rooms_max': 10}
        response = self.client.post('/api/plans/', data, format='json')
        assert response.status_code == 201
