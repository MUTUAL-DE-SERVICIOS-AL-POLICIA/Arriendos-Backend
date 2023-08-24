from rest_framework import serializers
from plans.models import Plan, Requirement, PlanRequirement


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = '__all__'


class PlanRequirementSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    requirement = RequirementSerializer()
    class Meta:
        model = PlanRequirement
        fields = '__all__'
        
