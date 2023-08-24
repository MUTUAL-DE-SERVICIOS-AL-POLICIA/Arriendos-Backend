from django.urls import path
from .views import (
    Rate_List_Create_View, Rate_Retrieve_Update_Destroy_View,
    Time_List_Create_View, Time_Retrieve_Update_Destroy_View,
    Product_List_Create_View, Product_Retrieve_Update_Destroy_View
)

urlpatterns = [
    path('', Product_List_Create_View.as_view(), name='product-list-create'),
    path('<int:pk>/', Product_Retrieve_Update_Destroy_View.as_view(), name='product-retrieve-update-destroy'),

    path('rates/', Rate_List_Create_View.as_view(), name='rate-list-create'),
    path('rates/<int:pk>/', Rate_Retrieve_Update_Destroy_View.as_view(), name='rate-retrieve-update-destroy'),

    path('times/', Time_List_Create_View.as_view(), name='time-list-create'),
    path('times/<int:pk>/', Time_Retrieve_Update_Destroy_View.as_view(), name='time-retrieve-update-destroy'),
]
