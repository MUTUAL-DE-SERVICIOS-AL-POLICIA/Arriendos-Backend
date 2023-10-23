from rest_framework import serializers
from financials.models import Payment
class Payment_Serializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields = '__all__'