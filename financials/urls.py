from django.urls import path
from financials.views import Register_payment,Register_warranty

urlpatterns = [
    path('register_payment/',Register_payment.as_view()),
    path('register_warranty/',Register_warranty.as_view())
]