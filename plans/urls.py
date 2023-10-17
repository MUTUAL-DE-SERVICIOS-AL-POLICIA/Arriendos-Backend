from django.urls import include, path
from rest_framework import routers
from plans.views import Plan_Api, Plan_Detail

urlpatterns = [
    path('', Plan_Api.as_view(), name='plans'),
    path('<int:pk>', Plan_Detail.as_view(), name='plans_detail'),
]