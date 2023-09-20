from django.urls import include, path
from rest_framework import routers
from .views import RateRequirement_Api, RateRequirement_Detail, All_Rates, RateWithRelatedDataView
urlpatterns = [
    path('rates/', RateRequirement_Api.as_view()),
    path('rates/<str:pk>', RateRequirement_Detail.as_view()),
    path('allrates/', RateWithRelatedDataView.as_view())   
]
