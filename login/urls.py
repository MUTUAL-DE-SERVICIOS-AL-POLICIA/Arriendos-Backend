from django.urls import include, path
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from login import views
urlpatterns = [
    path("connect_ldap/", views.connect_ldap)
]