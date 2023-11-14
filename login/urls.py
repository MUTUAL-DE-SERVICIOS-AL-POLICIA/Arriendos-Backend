from django.urls import include, path
from login import views
from .views import Users_Ldap
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("connect_ldap/", views.Connect_Ldap),
    path('auth/', views.Auth.as_view(), name='token_obtain_pair'),
    path('users_ldap/', Users_Ldap.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]