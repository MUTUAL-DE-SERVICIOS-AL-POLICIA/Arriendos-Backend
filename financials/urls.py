from django.urls import path
from financials.views import Register_payment
urlpatterns = [
    path('register_payment/',Register_payment.as_view())
    ]