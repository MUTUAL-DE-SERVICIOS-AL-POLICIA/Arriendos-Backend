from django.urls import include, path
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from users import views
from users.views import User_Ldap, Assign_Api, Assign_Detail, User_Delete


urlpatterns = [
    path('', User_Ldap.as_view()),
    path('state/<str:pk>', User_Delete.as_view()),
    path('get_user/',views.get_user),
    path('assign/', Assign_Api.as_view()),
    path('assign/<str:pk>', Assign_Detail.as_view()),
]