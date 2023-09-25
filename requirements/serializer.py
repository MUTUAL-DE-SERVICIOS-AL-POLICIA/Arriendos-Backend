from rest_framework import serializers
from .models import Requirement, PlanRequirement, RateRequirement
from plans.serializer import PlanSerializer
from products.serializers import RateSerializer
from products.models import Rate
from customers.serializer import Customer_typeSerializer
from customers.models import Customer_type
from rest_framework import serializers
class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = '__all__'

class PlanRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanRequirement
        fields = '__all__'

class PlanRequiremenstSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    requirement = RequirementSerializer()
    class Meta:
        model = PlanRequirement
        fields = '__all__'
class RateRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateRequirement
        fields = '__all__'

class RatesRequirementSerializer(serializers.ModelSerializer):
    requirement = RequirementSerializer(many=True)
    rate = serializers.StringRelatedField()
    customer_type = Customer_typeSerializer(many=True)

    class Meta:
        model = RateRequirement
        fields = '__all__'

class RateWithRelatedDataSerializer(serializers.ModelSerializer):
    customer_type = serializers.SerializerMethodField()
    requirements = serializers.SerializerMethodField()

    class Meta:
        model = Rate
        fields = '__all__'

    def get_customer_type(self, obj):
        return Customer_type.objects.filter(raterequirement__rate=obj, raterequirement__is_active=True).distinct().values_list('name', flat=True)

    def get_requirements(self, obj):
        return Requirement.objects.filter(raterequirement__rate=obj, raterequirement__is_active=True).distinct().values_list('requirement_name', flat=True)

