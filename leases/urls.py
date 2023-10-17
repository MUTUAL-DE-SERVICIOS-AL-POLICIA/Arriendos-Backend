from django.urls import include, path
from rest_framework import routers
from leases import views
from leases.views import Selected_Product_Api, Event_Api,Get_state, StateRentalListCreateView, List_state
urlpatterns = [
    path('', Selected_Product_Api.as_view()),
    path('event/', Event_Api.as_view()),
    path('get_state/', Get_state.as_view()),
    path('state/',StateRentalListCreateView.as_view()),
    path('list_state/',List_state.as_view()),
 ]