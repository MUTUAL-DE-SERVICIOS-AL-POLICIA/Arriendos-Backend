from rest_framework import serializers
from .models import Requirement, PlanRequirement, RateRequirement
from plans.serializer import PlanSerializer
from products.serializers import RateSerializer

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
    requirement = RequirementSerializer()
    rate = RateSerializer()
    class Meta:
        model = RateRequirement
        fields = '__all__'