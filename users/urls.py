from django.urls import include, path
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from users import views
from users.views import User_Ldap, Assing_Api, Assing_Detail


urlpatterns = [
    path('', User_Ldap.as_view()),
    path('get_user/',views.get_user),
    path('assing/', Assing_Api.as_view()),
    path('assing/<str:pk>', Assing_Detail.as_view()),
]