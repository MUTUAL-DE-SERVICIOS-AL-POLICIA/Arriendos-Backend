import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from plans.models import Plan


@pytest.mark.django_db
class TestPlanModels:
    def test_plan_creation(self):
        plan = Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=8, rooms_max=15)
        assert plan.plan_name == 'Plan A'
        assert plan.plan_discount == 25
        assert plan.rooms_min == 8
        assert plan.rooms_max == 15
        assert str(plan) == 'Plan A (8-15 ambientes)'

    def test_plan_no_discount(self):
        plan = Plan.objects.create(plan_name='Sin Plan', plan_discount=0, rooms_min=1, rooms_max=1)
        assert plan.plan_discount == 0
        assert str(plan) == 'Sin Plan (1-1 ambientes)'


@pytest.mark.django_db
class TestPlanAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_plan_list(self):
        Plan.objects.create(plan_name='Plan A', plan_discount=25, rooms_min=8, rooms_max=15)
        response = self.client.get('/api/plans/')
        assert response.status_code == 200

    def test_plan_create(self):
        data = {'plan_name': 'New Plan', 'plan_discount': 10, 'rooms_min': 1, 'rooms_max': 50}
        response = self.client.post('/api/plans/', data, format='json')
        assert response.status_code == 201
        assert Plan.objects.count() == 1