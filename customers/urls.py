from django.urls import include, path
from rest_framework import routers
from customers import views
from customers.views import Customer_Api, CustomerInsitution_Detail, Customer_Type_Api, Customer_Type_Detail, Contact_Detail, Contact_Api
urlpatterns = [
    path('', Customer_Api.as_view()),
    path('institution/<str:pk>', CustomerInsitution_Detail.as_view()),
    path('type/', Customer_Type_Api.as_view()),
    path('type/<str:pk>', Customer_Type_Detail.as_view()),
    path('contact/', Contact_Api.as_view()),
    path('contact/<str:pk>', Contact_Detail.as_view())
]