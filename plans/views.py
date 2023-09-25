from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Plan
from .serializer import PlanSerializer
from requirements.models import Requirement, PlanRequirement
from requirements.serializer import RequirementSerializer, PlanRequirementSerializer, PlanRequiremenstSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import math
from datetime import datetime

# Create your views here.
class Plan_Api(generics.GenericAPIView):
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    
    def get(self, request, *args, **kwargs):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        plans = Plan.objects.all()
        total_plans = plans.count()
        if search_param:
            plans = plans.filter(title__icontains=search_param)
        serializer = self.serializer_class(plans[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_plans,
            "page": page_num,
            "last_page": math.ceil(total_plans/ limit_num),
            'plans': serializer.data
        })
    
    def post(self, request, *args, **kw):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"plan": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class Plan_Detail(generics.GenericAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    def get_plan(self, pk, *args, **kwargs):
        try:
            return Plan.objects.get(pk=pk)
        except:
            return None
        
    def get(self, request, pk, *args, **kw):
        plan = self.get_plan(pk=pk)
        if plan == None:
            return Response({"status": "fail", "message": f"Plan with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(plan)
        return Response({"status": "success", "data": {"plan": serializer.data}}, status=status.HTTP_200_OK)
    
    def patch(self, request, pk, *args, **kw):
        plan = self.get_plan(pk)
        if plan == None:
            return Response({"status": "fail", "message": f"Plan with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"plan": serializer.data}}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)                
        
class Requirement_Api(generics.GenericAPIView):
    serializer_class = RequirementSerializer
    queryset = Requirement.objects.all()

    def get(self, request, *args, **kw):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        requirements = Requirement.objects.all().order_by('id')
        total_requirements = requirements.count()
        if search_param:
            requirements = requirements.filter(title__icontains=search_param)
        serializer = self.serializer_class(requirements[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_requirements,
            "page": page_num,
            "last_page": math.ceil(total_requirements/ limit_num),
           'requirements': serializer.data,
        })
    
    def post(self, request, *args, **kw):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"requirement": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
class Requirement_Detail(generics.GenericAPIView):
    queryset = Requirement.objects.all()
    serializer_class = RequirementSerializer

    def get_requirement(self, pk, *args, **kw):
        try:
            return Requirement.objects.get(pk=pk)
        except:
            return None
        
    def get(self, request, pk, *args, **kw):
        requirement = self.get_requirement(pk=pk)
        if requirement == None:
            return Response({"status": "fail", "message": f"Requirement with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(requirement)
        return Response({"status": "success", "data": {"requirement": serializer.data}}, status=status.HTTP_200_OK)
    
    def patch(self, request, pk, *args, **kw):
        requirement = self.get_requirement(pk)
        if requirement == None:
            return Response({"status": "fail", "message": f"Requirement with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(requirement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"requirement": serializer.data}}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        


class PlanRequirement_Api(generics.GenericAPIView):
    queryset = PlanRequirement.objects.all
    serializer_class = PlanRequirementSerializer

    def get(self, request, *args, **kw):
        serializer_class = PlanRequiremenstSerializer
        queryset = PlanRequirement.objects.all()
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        plan_requirements = PlanRequirement.objects.all()
        total_plan_requirements = plan_requirements.count()
        if search_param:
            plan_requirements = plan_requirements.filter(title__icontains=search_param)
        serializer = serializer_class(plan_requirements[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_plan_requirements,
            "page": page_num,
            "last_page": math.ceil(total_plan_requirements/ limit_num),
            "plan_requirements": serializer.data
        })
    
    def post(self, request, *args, **kw):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"plan_requirement": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
class PlanRequirement_Detail(generics.GenericAPIView):
    queryset = PlanRequirement.objects.all()
    serializer_class = PlanRequirementSerializer

    def get_plan_requirement(self, request, pk, *args, **kw):
        try:
            return PlanRequirement.objects.get(pk=pk)
        except:
            return None
        
    def get(self, request, pk, *args, **kw):
        plan_requirement = self.get_plan_requirement(pk=pk)
        if plan_requirement == None:
            return Response({"status": "fail", "message": f"Plan Requirement with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(plan_requirement)
        return Response({"status": "success", "data": {"plan_requirement": serializer.data}}, status=status.HTTP_200_OK)

    def patch(self, request, pk, *args, **kw):
        plan_requirement = self.get_plan_requirement(pk)
        if plan_requirement == None:
            return Response({"status": "fail", "message": f"Plan Requirement with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(plan_requirement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"plan_requirement": serializer.data}}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        