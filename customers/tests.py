import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from customers.models import Customer, Customer_type


@pytest.mark.django_db
class TestCustomerAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.institution_ct = Customer_type.objects.create(name='Institución', is_institution=True, is_police=False)
        self.regular_ct = Customer_type.objects.create(name='Público', is_institution=False, is_police=False)

    def test_customer_create(self):
        data = {
            'customer_type': self.institution_ct.id,
            'institution': {
                'name': 'New Co',
                'nit': '9999999',
                'contacts': [
                    {'name': 'Contact1', 'ci_nit': '1234567', 'phone': '7777777'}
                ]
            }
        }
        response = self.client.post('/api/customers/', data, format='json')
        assert response.status_code == 201
        assert Customer.objects.count() == 1

    def test_customer_update(self):
        customer = Customer.objects.create(institution_name='Old Name', nit='1111111', customer_type=self.institution_ct)
        response = self.client.patch(f'/api/customers/{customer.id}', {'institution': {'name': 'New Name', 'nit': '1111111', 'contacts': []}}, format='json')
        assert response.status_code == 200
        customer.refresh_from_db()
        assert customer.institution_name == 'New Name'

    def test_customer_create_non_institution(self):
        data = {
            'customer_type': self.regular_ct.id,
            'customer': {
                'name': 'Juan Perez',
                'ci_nit': '12345678',
                'phone': '70000001'
            }
        }
        response = self.client.post('/api/customers/', data, format='json')
        assert response.status_code == 201

    def test_customer_type_update(self):
        ct = Customer_type.objects.create(name='Old Name')
        response = self.client.patch(f'/api/customers/type/{ct.id}', {'name': 'New Name'}, format='json')
        assert response.status_code == 200
        ct.refresh_from_db()
        assert ct.name == 'New Name'
