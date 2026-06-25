from django.urls import path
from .views import (
    Module_List_View,
    Permission_List_View,
    Role_List_Create_View,
    Role_Detail_View,
    UserRole_Assign_View,
    UserRole_List_View,
    UserRole_Detail_View,
    MyPermissions_View,
)

urlpatterns = [
    path('modules/', Module_List_View.as_view(), name='module-list'),
    path('permissions/', Permission_List_View.as_view(), name='permission-list'),

    path('', Role_List_Create_View.as_view(), name='role-list-create'),
    path('<int:pk>', Role_Detail_View.as_view(), name='role-detail'),

    path('assign/', UserRole_Assign_View.as_view(), name='user-role-assign'),
    path('assignments/', UserRole_List_View.as_view(), name='user-role-list'),
    path('assignments/<int:pk>', UserRole_Detail_View.as_view(), name='user-role-detail'),

    path('my-permissions/', MyPermissions_View.as_view(), name='my-permissions'),
]
