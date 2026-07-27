import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from plans.models import Plan


@pytest.mark.django_db
class TestPlanAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_plan_create(self):
        data = {'plan_name': 'New Plan', 'plan_discount': 10, 'rooms_min': 1, 'rooms_max': 50}
        response = self.client.post('/api/plans/', data, format='json')
        assert response.status_code == 201
        assert Plan.objects.count() == 1
