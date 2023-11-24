from django.urls import path
from .views import PropertyListCreateView, PropertyRetrieveUpdateDestroyView, RoomListCreateView, RoomRetrieveUpdateDestroyView, List_Properties_with_Rooms, Sub_Room_Api, Sub_Room_Detail

urlpatterns = [
    path('properties/', PropertyListCreateView.as_view(), name='property-list-create'),
    path('properties/<int:pk>/', PropertyRetrieveUpdateDestroyView.as_view(), name='property-retrieve-update-destroy'),
    path('', RoomListCreateView.as_view(), name='room-list-create'),
    path('<int:pk>/', RoomRetrieveUpdateDestroyView.as_view(), name='room-retrieve-update-destroy'),
    path('properties/roomslist/', List_Properties_with_Rooms.as_view(), name='List_Properties_with_Rooms'),
    path('sub_rooms/', Sub_Room_Api.as_view()),
    path('sub_rooms/<str:pk>',Sub_Room_Detail.as_view())
]