from django.urls import include, path
from rest_framework import routers
from leases import views
from leases.views import Selected_Product_Api
urlpatterns = [
    path('', Selected_Product_Api.as_view()),
 ]