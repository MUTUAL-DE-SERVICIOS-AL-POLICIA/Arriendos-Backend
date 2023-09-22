from django.urls import path
from .views import PropertyListCreateView, PropertyRetrieveUpdateDestroyView, RoomListCreateView, RoomRetrieveUpdateDestroyView, List_Properties_with_Rooms

urlpatterns = [
    path('properties/', PropertyListCreateView.as_view(), name='property-list-create'),
    path('properties/<int:pk>/', PropertyRetrieveUpdateDestroyView.as_view(), name='property-retrieve-update-destroy'),
    path('', RoomListCreateView.as_view(), name='room-list-create'),
    path('<int:pk>/', RoomRetrieveUpdateDestroyView.as_view(), name='room-retrieve-update-destroy'),
    path('properties/roomslist/', List_Properties_with_Rooms, name='List_Properties_with_Rooms'),
]