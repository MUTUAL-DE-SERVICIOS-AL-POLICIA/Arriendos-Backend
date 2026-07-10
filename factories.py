import factory
from django.contrib.auth.models import User
from rooms.models import Property, Room, Sub_Room
from customers.models import Customer_type, Customer, Contact
from products.models import Rate, HourRange, Product, Price, Price_Additional_Hour
from plans.models import Plan
from leases.models import State, Rental, Event_Type, Selected_Product
from requirements.models import Requirement, RateRequirement
from financials.models import Payment, Warranty_Movement
from roles.models import Module, Permission, Role, RolePermission, UserRole
from users.models import Record


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    email = factory.LazyAttribute(lambda o: f'{o.username}@test.com')


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Module

    name = factory.Sequence(lambda n: f'Module {n}')
    codename = factory.Sequence(lambda n: f'module_{n}')
    description = factory.Faker('sentence')


class PermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permission

    name = factory.Sequence(lambda n: f'Permission {n}')
    codename = factory.Sequence(lambda n: f'perm_{n}')
    description = factory.Faker('sentence')


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    name = factory.Sequence(lambda n: f'Role {n}')
    description = factory.Faker('sentence')


class PropertyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Property

    name = factory.Sequence(lambda n: f'Property {n}')
    address = factory.Faker('address')
    department = factory.Faker('city')


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    name = factory.Sequence(lambda n: f'Room {n}')
    capacity = factory.Faker('random_int', min=10, max=100)
    warranty = factory.Faker('pyfloat', min_value=100, max_value=5000)
    property = factory.SubFactory(PropertyFactory)


class SubRoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Sub_Room

    name = factory.Sequence(lambda n: f'SubRoom {n}')
    quantity = factory.Faker('random_int', min=1, max=20)
    room = factory.SubFactory(RoomFactory)


class CustomerTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer_type

    name = factory.Sequence(lambda n: f'CustomerType {n}')
    is_institution = False
    is_police = False


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    institution_name = factory.Sequence(lambda n: f'Customer {n}')
    nit = factory.Sequence(lambda n: f'{1000000 + n}')
    customer_type = factory.SubFactory(CustomerTypeFactory)


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact

    name = factory.Faker('name')
    ci_nit = factory.Sequence(lambda n: f'{2000000 + n}')
    phone = factory.Sequence(lambda n: f'7000000{n % 10}')
    customer = factory.SubFactory(CustomerFactory)


class RateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rate

    name = factory.Sequence(lambda n: f'Rate {n}')


class HourRangeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HourRange

    time = factory.Sequence(lambda n: (n + 1) * 2)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    day = factory.Lambda(lambda: ['LUNES', 'MARTES', 'MIERCOLES'])
    rate = factory.SubFactory(RateFactory)
    room = factory.SubFactory(RoomFactory)
    hour_range = factory.SubFactory(HourRangeFactory)


class PriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Price

    mount = factory.Faker('pyfloat', min_value=100, max_value=10000)
    product = factory.SubFactory(ProductFactory)


class PlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Plan

    plan_name = factory.Sequence(lambda n: f'Plan {n}')
    plan_discount = factory.Faker('pyfloat', min_value=0, max_value=50)
    rooms_min = 1
    rooms_max = 100


class StateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = State

    name = factory.Sequence(lambda n: f'State {n}')
    next_state = factory.Lambda(lambda: [])


class EventTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event_Type

    name = factory.Sequence(lambda n: f'Event {n}')


class RentalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rental

    initial_total = factory.Faker('pyfloat', min_value=500, max_value=10000)
    contract_number = factory.Sequence(lambda n: f'CTR-{2024}-{n:04d}')
    customer = factory.SubFactory(CustomerFactory)
    state = factory.SubFactory(StateFactory)
    plan = factory.SubFactory(PlanFactory)


class SelectedProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Selected_Product

    start_time = factory.LazyFunction(lambda: __import__('django.utils.timezone').now())
    end_time = factory.LazyFunction(lambda: __import__('django.utils.timezone').now())
    product_price = factory.Faker('pyfloat', min_value=100, max_value=5000)
    rental = factory.SubFactory(RentalFactory)
    product = factory.SubFactory(ProductFactory)
    event_type = factory.SubFactory(EventTypeFactory)


class RequirementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Requirement

    requirement_name = factory.Sequence(lambda n: f'Requirement {n}')
    is_active = True


class RateRequirementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RateRequirement

    rate = factory.SubFactory(RateFactory)
    requirement = factory.SubFactory(RequirementFactory)
    customer_type = factory.SubFactory(CustomerTypeFactory)


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    voucher_number = factory.Sequence(lambda n: f'VCH-{n:05d}')
    business_name = factory.Faker('company')
    nit = factory.Sequence(lambda n: f'{3000000 + n}')
    detail = factory.Faker('sentence')
    payable_mount = factory.Faker('pyfloat', min_value=100, max_value=5000)
    amount_paid = factory.Faker('pyfloat', min_value=100, max_value=5000)
    rental = factory.SubFactory(RentalFactory)


class WarrantyMovementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Warranty_Movement

    voucher_number = factory.Sequence(lambda n: f'WRN-{n:05d}')
    income = factory.Faker('pyfloat', min_value=100, max_value=5000)
    discount = 0
    returned = 0
    balance = factory.Faker('pyfloat', min_value=100, max_value=5000)
    detail = factory.Faker('sentence')
    rental = factory.SubFactory(RentalFactory)


class RecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Record

    action = 'create'
    model = 'TestModel'
    detail = factory.Faker('sentence')
    instance_id = 1
    user = factory.SubFactory(UserFactory)
