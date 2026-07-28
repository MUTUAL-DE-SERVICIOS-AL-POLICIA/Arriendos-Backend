import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from customers.models import Customer, Customer_type, Contact


@pytest.mark.django_db
class TestCustomerCreateInstitution:
    """POST /api/customers/ — crear cliente institución"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.inst_ct = Customer_type.objects.create(name='Institución', is_institution=True, is_police=False)
        self.regular_ct = Customer_type.objects.create(name='Público', is_institution=False, is_police=False)

    def test_create_institution_success(self):
        data = {
            'customer_type': self.inst_ct.id,
            'institution': {
                'name': 'Ministerio',
                'nit': '1234567890',
                'contacts': [{'name': 'Juan', 'ci_nit': '111', 'phone': '7777777'}]
            }
        }
        response = self.client.post('/api/customers/', data, format='json')
        assert response.status_code == 201
        assert Customer.objects.count() == 1
        assert Contact.objects.filter(customer__id=Customer.objects.first().id).count() == 1

    def test_create_institution_missing_contacts_returns_400(self):
        data = {
            'customer_type': self.inst_ct.id,
            'institution': {
                'name': 'Min',
                'nit': '1111111111',
                'contacts': []
            }
        }
        response = self.client.post('/api/customers/', data, format='json')
        assert response.status_code == 400
        assert 'contacto' in response.data['error'].lower()

    def test_create_institution_duplicate_nit_returns_400(self):
        Customer.objects.create(institution_name='Existente', nit='1234567890', customer_type=self.inst_ct)
        data = {
            'customer_type': self.inst_ct.id,
            'institution': {
                'name': 'Dup',
                'nit': '1234567890',
                'contacts': [{'name': 'X', 'ci_nit': '222', 'phone': '7777777'}]
            }
        }
        response = self.client.post('/api/customers/', data, format='json')
        assert response.status_code == 400
        assert 'registrada' in response.data['error'].lower()

    def test_create_institution_missing_name_returns_400(self):
        data = {
            'customer_type': self.inst_ct.id,
            'institution': {
                'nit': '9999999999',
                'contacts': [{'name': 'X', 'ci_nit': '333', 'phone': '7777777'}]
            }
        }
        response = self.client.post('/api/customers/', data, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestCustomerCreateNonInstitution:
    """POST /api/customers/ — crear cliente público"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.regular_ct = Customer_type.objects.create(name='Público', is_institution=False, is_police=False)

    def test_create_regular_customer_success(self):
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
        assert Customer.objects.count() == 1
        contact = Contact.objects.first()
        assert contact.name == 'Juan Perez'

    def test_create_regular_customer_duplicate_ci_returns_400(self):
        ct = Customer.objects.create(customer_type=self.regular_ct)
        Contact.objects.create(name='Existente', ci_nit='12345678', phone='7777777', customer=ct)
        data = {
            'customer_type': self.regular_ct.id,
            'customer': {
                'name': 'Dup',
                'ci_nit': '12345678',
                'phone': '70000002'
            }
        }
        response = self.client.post('/api/customers/', data, format='json')
        assert response.status_code == 400
        assert 'existe' in response.data['error'].lower()

    def test_create_regular_customer_missing_fields_returns_400(self):
        data = {
            'customer_type': self.regular_ct.id,
            'customer': {'name': 'Sin campos'}
        }
        response = self.client.post('/api/customers/', data, format='json')
        assert response.status_code == 400

    def test_create_customer_invalid_type_returns_404(self):
        data = {'customer_type': 99999, 'customer': {'name': 'X', 'ci_nit': '1', 'phone': '7'}}
        response = self.client.post('/api/customers/', data, format='json')
        assert response.status_code == 404


@pytest.mark.django_db
class TestCustomerDetail:
    """PATCH/DELETE /api/customers/<pk>"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)
        self.inst_ct = Customer_type.objects.create(name='Institución', is_institution=True)
        self.regular_ct = Customer_type.objects.create(name='Público', is_institution=False)

    def test_patch_institution_success(self):
        customer = Customer.objects.create(institution_name='Old', nit='111', customer_type=self.inst_ct)
        Contact.objects.create(name='C1', ci_nit='222', phone='777', customer=customer, is_customer=False)
        data = {
            'institution': {
                'name': 'New Name',
                'nit': '111',
                'contacts': [{'id': customer.contact_set.first().id, 'name': 'C1', 'ci_nit': '222', 'phone': '777'}]
            }
        }
        response = self.client.patch(f'/api/customers/{customer.id}', data, format='json')
        assert response.status_code == 200
        customer.refresh_from_db()
        assert customer.institution_name == 'New Name'

    def test_patch_nonexistent_customer_returns_404(self):
        response = self.client.patch('/api/customers/99999', {'institution': {'name': 'X', 'nit': '0', 'contacts': []}}, format='json')
        assert response.status_code == 404

    def test_delete_customer_success(self):
        customer = Customer.objects.create(institution_name='Del', nit='999', customer_type=self.inst_ct)
        response = self.client.delete(f'/api/customers/{customer.id}')
        assert response.status_code == 204
        assert Customer.objects.count() == 0

    def test_delete_customer_with_active_rental_returns_400(self):
        from leases.models import State, Rental
        State.objects.get_or_create(id=3, defaults={'name': 'Alquilado', 'next_state': []})
        customer = Customer.objects.create(institution_name='ConArriendo', nit='888', customer_type=self.inst_ct)
        Rental.objects.create(initial_total=1000, customer=customer, state_id=3)
        response = self.client.delete(f'/api/customers/{customer.id}')
        assert response.status_code == 400
        assert 'alquiler activo' in response.data['error'].lower()

    def test_delete_customer_with_annulled_rental_allowed(self):
        from leases.models import State, Rental
        State.objects.get_or_create(id=5, defaults={'name': 'Anulado', 'next_state': []})
        customer = Customer.objects.create(institution_name='Anulado', nit='777', customer_type=self.inst_ct)
        Rental.objects.create(initial_total=1000, customer=customer, state_id=5)
        response = self.client.delete(f'/api/customers/{customer.id}')
        assert response.status_code == 204

    def test_delete_nonexistent_customer_returns_404(self):
        response = self.client.delete('/api/customers/99999')
        assert response.status_code == 404


@pytest.mark.django_db
class TestCustomerTypeApi:
    """POST/PATCH /api/customers/type/"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_create_customer_type_success(self):
        response = self.client.post('/api/customers/type/', {'name': 'Nuevo Tipo'}, format='json')
        assert response.status_code == 201
        assert Customer_type.objects.count() == 1

    def test_patch_customer_type_success(self):
        ct = Customer_type.objects.create(name='Old')
        response = self.client.patch(f'/api/customers/type/{ct.id}', {'name': 'New'}, format='json')
        assert response.status_code == 200
        ct.refresh_from_db()
        assert ct.name == 'New'

    def test_patch_nonexistent_type_returns_404(self):
        response = self.client.patch('/api/customers/type/99999', {'name': 'X'}, format='json')
        assert response.status_code == 404

    def test_get_customer_types_with_search(self):
        Customer_type.objects.create(name='Policía')
        Customer_type.objects.create(name='Civil')
        response = self.client.get('/api/customers/type/?search=policía')
        assert response.status_code == 200
        assert response.data['total'] == 1

    def test_get_customer_types_pagination(self):
        for i in range(15):
            Customer_type.objects.create(name=f'Type {i}')
        response = self.client.get('/api/customers/type/?page=0&limit=5')
        assert response.status_code == 200
        assert len(response.data['customer_type']) == 5
        assert response.data['total'] == 15


@pytest.mark.django_db
class TestCustomerFilterOptions:
    """GET /api/customers/filter_options/"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin', password='admin123')
        self.client.force_authenticate(user=self.user)

    def test_filter_options_returns_types(self):
        Customer_type.objects.create(name='Tipo1')
        Customer_type.objects.create(name='Tipo2')
        response = self.client.get('/api/customers/filter_options/')
        assert response.status_code == 200
        assert len(response.data['customer_types']) == 2
