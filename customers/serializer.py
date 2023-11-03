from rest_framework import serializers
from .models import Customer, Customer_type, Contact

class Customer_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer_type
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
class CustomersSerializer(serializers.ModelSerializer):
    customer_type = Customer_typeSerializer()
    contacts = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = '__all__'
    def get_contacts(self, obj):
        contacts = Contact.objects.filter(customer_id=obj, is_active=True).order_by('id')
        contact_serializer = ContactSerializer(contacts, many=True)
        return contact_serializer.data
