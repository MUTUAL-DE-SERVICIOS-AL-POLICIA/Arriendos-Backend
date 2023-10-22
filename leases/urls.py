from django.urls import include, path
from leases.views import Pre_Reserve_Api, Selected_Product_Calendar_Api, Event_Api,Get_state, StateRentalListCreateView, List_state,Change_state,Get_Rental,Register_payment

urlpatterns = [
    path('', Pre_Reserve_Api.as_view()),
    path('calendar/', Selected_Product_Calendar_Api.as_view()),
    path('event/', Event_Api.as_view()),
    path('get_rental_information/',Get_Rental.as_view() ),
    path('get_state/', Get_state.as_view()),
    path('state/',StateRentalListCreateView.as_view()),
    path('list_state/',List_state.as_view()),
    path('change_state/', Change_state.as_view()),
    path('register_payment/',Register_payment.as_view())
    ]