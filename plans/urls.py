from django.urls import include, path
from rest_framework import routers
from plans import views
from plans.views import Plan_Api, Plan_Detail, Requirement_Api, Requirement_Detail, PlanRequirement_Api, PlanRequirement_Detail

urlpatterns = [
    path('', Plan_Api.as_view(), name='plans'),
    path('<int:pk>', Plan_Detail.as_view(), name='plans_detail'),
    path('requirements/', Requirement_Api.as_view(), name='requirements'),
    path('requirements/<int:pk>', Requirement_Detail.as_view(), name='requirements_detail'),
    path('plan_requirements/', PlanRequirement_Api.as_view(), name='plan_requirements'),
    path('plan_requirements/<int:pk>', PlanRequirement_Detail.as_view(), name='plan_requirements_detail'),
]