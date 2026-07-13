import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from customers.models import Customer, Customer_type, Contact


@pytest.mark.django_db
class TestCustomerModels:
    def test_customer_type_creation(self):
        ct = Customer_type.objects.create(name='Público', is_institution=False, is_police=False)
        assert ct.name == 'Público'
        assert str(ct) == 'Público'

    def test_customer_creation(self):
        ct = Customer_type.objects.create(name='Público')
        customer = Customer.objects.create(
            institution_name='Test Company',
            nit='1234567',
            customer_type=ct
        )
        assert customer.institution_name == 'Test Company'
        assert 'Test Company' in str(customer)
        assert '1234567' in str(customer)

    def test_contact_creation(self):
        ct = Customer_type.objects.create(name='Público')
        customer = Customer.objects.create(institution_name='Test', nit='1234567', customer_type=ct)
        contact = Contact.objects.create(
            name='John Doe',
            ci_nit='7654321',
            phone='70000001',
            customer=customer
        )
        assert contact.name == 'John Doe'
        assert 'John Doe' in str(contact)
        assert '7654321' in str(contact)


@pytest.mark.django_db
class TestCustomerAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        # Create institution customer type for testing
        self.institution_ct = Customer_type.objects.create(name='Institución', is_institution=True, is_police=False)
        self.regular_ct = Customer_type.objects.create(name='Público', is_institution=False, is_police=False)

    def test_customer_list(self):
        Customer.objects.create(institution_name='Test Co', nit='1234567', customer_type=self.regular_ct)
        response = self.client.get('/api/customers/')
        assert response.status_code == 200

    def test_customer_search_by_nit(self):
        Customer.objects.create(institution_name='Test Co', nit='1234567', customer_type=self.regular_ct)
        response = self.client.get('/api/customers/?search_nit=1234567')
        assert response.status_code == 200

    def test_customer_search_by_name(self):
        Customer.objects.create(institution_name='Bolivian Express', nit='1234567', customer_type=self.regular_ct)
        response = self.client.get('/api/customers/?search_name=Bolivian')
        assert response.status_code == 200

    def test_customer_type_list(self):
        Customer_type.objects.create(name='Público')
        Customer_type.objects.create(name='Policial Activo')
        response = self.client.get('/api/customers/type/')
        assert response.status_code == 200

    def test_customer_filter_options(self):
        response = self.client.get('/api/customers/filter_options/')
        assert response.status_code == 200
        assert 'customer_types' in response.data

    def test_customer_create(self):
        data = {
            'customer_type': self.institution_ct.id,
            'institution': {
                'name': 'New Co',
                'nit': '9999999',
                'contacts': []
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

    def test_customer_delete(self):
        customer = Customer.objects.create(institution_name='ToDelete', nit='2222222', customer_type=self.institution_ct)
        response = self.client.delete(f'/api/customers/{customer.id}')
        assert response.status_code == 200

    def test_customer_type_create(self):
        data = {'name': 'Nuevo Tipo', 'is_institution': False, 'is_police': False}
        response = self.client.post('/api/customers/type/', data, format='json')
        assert response.status_code == 201

    def test_customer_type_detail(self):
        ct = Customer_type.objects.create(name='Test Type')
        response = self.client.get(f'/api/customers/type/{ct.id}')
        assert response.status_code == 200

    def test_customer_type_detail_not_found(self):
        response = self.client.get('/api/customers/type/9999')
        assert response.status_code == 404

    def test_customer_type_update(self):
        ct = Customer_type.objects.create(name='Old Name')
        response = self.client.patch(f'/api/customers/type/{ct.id}', {'name': 'New Name'}, format='json')
        assert response.status_code == 200
        ct.refresh_from_db()
        assert ct.name == 'New Name'

    def test_customer_type_update_not_found(self):
        response = self.client.patch('/api/customers/type/9999', {'name': 'X'}, format='json')
        assert response.status_code == 404

    def test_customer_type_list_search(self):
        Customer_type.objects.create(name='Policial Activo')
        Customer_type.objects.create(name='Publico')
        response = self.client.get('/api/customers/type/?search=Policial')
        assert response.status_code == 200

    def test_customer_type_list_limit_all(self):
        Customer_type.objects.create(name='Type1')
        response = self.client.get('/api/customers/type/?limit=-1')
        assert response.status_code == 200

    def test_customer_list_limit_all(self):
        Customer.objects.create(institution_name='C1', nit='111', customer_type=self.regular_ct)
        response = self.client.get('/api/customers/?limit=-1')
        assert response.status_code == 200

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