from django.urls import path
from .views import Records_View, AvailableByRentalApi

urlpatterns = [
    path('', Records_View.as_view(), name='records'),
    path('available_by_rental/', AvailableByRentalApi.as_view(), name='available-by-rental'),
]
