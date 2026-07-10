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


@pytest.mark.django_db
class TestCustomerAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.ct = Customer_type.objects.create(name='Público')

    def test_customer_list(self):
        Customer.objects.create(institution_name='Test Co', nit='1234567', customer_type=self.ct)
        response = self.client.get('/api/customers/')
        assert response.status_code == 200

    def test_customer_search_by_nit(self):
        Customer.objects.create(institution_name='Test Co', nit='1234567', customer_type=self.ct)
        response = self.client.get('/api/customers/?search_nit=1234567')
        assert response.status_code == 200

    def test_customer_search_by_name(self):
        Customer.objects.create(institution_name='Bolivian Express', nit='1234567', customer_type=self.ct)
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
