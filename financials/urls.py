from django.urls import path
from financials.views import Register_payment,Register_warranty,Discount_warranty

urlpatterns = [
    path('register_payment/',Register_payment.as_view()),
    path('register_warranty/',Register_warranty.as_view()),
    path('discount_warranty/',Discount_warranty.as_view())
]