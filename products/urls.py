from django.urls import path
from .views import (
    Rate_Api, Rate_Detail,
    HourRange_List_Create_View, HourRange_Retrieve_Update_Destroy_View,
    Product_Api,
    Price_List_Create_View,
    Price_Retrieve_Update_Destroy_View
)

urlpatterns = [
    path('', Product_Api.as_view(), name='product-list-create'),
    path('<int:pk>', Product_Api.as_view(), name='product-retrieve-update-destroy'),

    path('rates/', Rate_Api.as_view(), name='rate-list-create'),
    path('rates/<int:pk>', Rate_Detail.as_view()),

    path('hour-range/', HourRange_List_Create_View.as_view(), name='time-list-create'),
    path('hour-range/<int:pk>', HourRange_Retrieve_Update_Destroy_View.as_view(), name='range-retrieve-update-destroy'),

    path('price/', Price_List_Create_View.as_view(), name="price-list-create"),
    path('price/<int:pk>', Price_Retrieve_Update_Destroy_View.as_view(), name="price-retrieve-update-destroy")
]
