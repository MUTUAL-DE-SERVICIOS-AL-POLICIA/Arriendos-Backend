from django.urls import include, path
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from login import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("connect_ldap/", views.Connect_Ldap),
    path("search_ldap/", views.Search_User_Ldap),
    path('auth/', views.Auth.as_view(), name='token_obtain_pair'),
    path('users_ldap/', views.Users_ldap),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]