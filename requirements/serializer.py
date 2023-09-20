from rest_framework import serializers
from .models import Requirement, PlanRequirement, RateRequirement
from plans.serializer import PlanSerializer
from products.serializers import RateSerializer
from products.models import Rate
from customers.serializer import Customer_typeSerializer
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
class RatesRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateRequirement
        fields = '__all__'

class RateRequirementSerializer(serializers.ModelSerializer):
    requirement = RequirementSerializer(many=True)
    rate = serializers.StringRelatedField()
    customer_type = Customer_typeSerializer(many=True)

    class Meta:
        model = RateRequirement
        fields = '__all__'
        
class RateWithRelatedDataSerializer(serializers.ModelSerializer):
    rate_requirements = RateRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Rate
        fields = '__all__'