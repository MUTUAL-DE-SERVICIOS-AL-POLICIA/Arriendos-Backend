from django.urls import path
from .views import (
    Rate_Api,
    HourRange_List_Create_View, HourRange_Retrieve_Update_Destroy_View,
    Product_Api,
    Price_List_Create_View,
    Price_Retrieve_Update_Destroy_View,
    Posible_product,
    Additional_Hour_List_Create_View,
    Additional_Hour_Retrieve_Update_Destroy_View,
    Get_price_additional_hour,
    ProductFilterView
)

urlpatterns = [
    path('', Product_Api.as_view(), name='product-list-create'),
    path('<int:pk>', Product_Api.as_view(), name='product-retrieve-update-destroy'),

    path('product_filter/', ProductFilterView.as_view(), name='product-filter'),

    path('rates/', Rate_Api.as_view(), name='rate-list-create'),

    path('hour-range/', HourRange_List_Create_View.as_view(), name='time-list-create'),
    path('hour-range/<int:pk>', HourRange_Retrieve_Update_Destroy_View.as_view(), name='range-retrieve-update-destroy'),

    path('price/', Price_List_Create_View.as_view(), name="price-list-create"),
    path('price/<int:pk>', Price_Retrieve_Update_Destroy_View.as_view(), name="price-retrieve-update-destroy"),

    path('additional_hour/',Additional_Hour_List_Create_View.as_view()),
    path('additional_hour/<int:pk>', Additional_Hour_Retrieve_Update_Destroy_View.as_view()),
    path('get_price_additional_hour/',Get_price_additional_hour.as_view()),

    path("posible_product/", Posible_product.as_view())

]
