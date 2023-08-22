from django.urls import include, path
from rest_framework import routers
from customers import views
from customers.views import Customer_api, CustomerDetail, Customer_type_api, Customer_typeDetail

urlpatterns = [
    path('', Customer_api.as_view()),
    path('<str:pk>', CustomerDetail.as_view()),
    path('type/', Customer_type_api.as_view()),
    path('type/<str:pk>', Customer_typeDetail.as_view()),
]