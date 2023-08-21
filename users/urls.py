from django.urls import include, path
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from login import views
from users.views import User_Ldap

urlpatterns = [
    path('', User_Ldap.as_view()),

]