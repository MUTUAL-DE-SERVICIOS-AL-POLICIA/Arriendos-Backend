from django.urls import path
from .views import (
    RateListCreateView, RateRetrieveUpdateDestroyView,
    TimeListCreateView, TimeRetrieveUpdateDestroyView,
    ProductListCreateView, ProductRetrieveUpdateDestroyView
)

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy'),

    path('rates/', RateListCreateView.as_view(), name='rate-list-create'),
    path('rates/<int:pk>/', RateRetrieveUpdateDestroyView.as_view(), name='rate-retrieve-update-destroy'),

    path('times/', TimeListCreateView.as_view(), name='time-list-create'),
    path('times/<int:pk>/', TimeRetrieveUpdateDestroyView.as_view(), name='time-retrieve-update-destroy'),
]
