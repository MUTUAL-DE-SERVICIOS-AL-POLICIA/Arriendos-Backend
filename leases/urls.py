from django.urls import include, path
from leases.views import Pre_Reserve_Api, Selected_Product_Calendar_Api, Event_Api,Get_state, StateRentalListCreateView, List_state

urlpatterns = [
    path('', Pre_Reserve_Api.as_view()),
    path('calendar/', Selected_Product_Calendar_Api.as_view()),
    path('event/', Event_Api.as_view()),
    path('get_state/', Get_state.as_view()),
    path('state/',StateRentalListCreateView.as_view()),
    path('list_state/',List_state.as_view()),
    ]