from django.urls import path
from .views import PropertyListCreateView, PropertyRetrieveUpdateDestroyView, RoomListCreateView, RoomRetrieveUpdateDestroyView, List_Rooms_Properties

urlpatterns = [
    path('properties/', PropertyListCreateView.as_view(), name='property-list-create'),
    path('properties/<int:pk>/', PropertyRetrieveUpdateDestroyView.as_view(), name='property-retrieve-update-destroy'),
    path('rooms/', RoomListCreateView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', RoomRetrieveUpdateDestroyView.as_view(), name='room-retrieve-update-destroy'),
    path('properties/<int:id_number>/rooms/', List_Rooms_Properties, name='list_rooms_properties'),
]