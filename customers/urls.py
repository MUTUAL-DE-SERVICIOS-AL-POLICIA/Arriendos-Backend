from django.urls import include, path
from rest_framework import routers
from customers import views
from customers.views import *
urlpatterns = [
    path('', Customer_Api.as_view()),
    path('<str:pk>', Customer_Detail.as_view()),
    path('type/', Customer_Type_Api.as_view()),
    path('type/<str:pk>', Customer_Type_Detail.as_view()),
    path('identify_police/<str:parametro>/', identify_police.as_view(), name='consumir_microservicio'),
]