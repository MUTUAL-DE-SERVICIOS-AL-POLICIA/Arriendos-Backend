from django.urls import include, path
from rest_framework import routers
from .views import Requirement_Api, Requirement_Detail, RateRequirement_Api, RateRequirement_Detail, RateWithRelatedDataView,Requirements_customer,Register_delivered_requirement

urlpatterns = [
    path('', Requirement_Api.as_view(), name='requirements'),
    path('<int:pk>', Requirement_Detail.as_view(), name='requirements_detail'),
    path('rates/', RateRequirement_Api.as_view()),
    path('rates/<str:pk>', RateRequirement_Detail.as_view()),
    path('allrates/', RateWithRelatedDataView.as_view()),
    path('customer/', Requirements_customer.as_view() ),
    path('register_delivered_requirements',Register_delivered_requirement.as_view())
]
