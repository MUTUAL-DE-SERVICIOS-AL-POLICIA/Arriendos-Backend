from django.urls import include, path
from rest_framework import routers
from plans.views import Plan_Api

urlpatterns = [
    path('', Plan_Api.as_view()),
]