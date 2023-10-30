from django.urls import path
from financials.views import Register_payment,Register_warranty,Discount_warranty, Warranty_Returned, Register_total_payment

urlpatterns = [
    path('register_payment/',Register_payment.as_view()),
    path('register_payment/<int:rental_id>/',Register_payment.as_view()),
    path("register_total_payment/", Register_total_payment.as_view()),
    path('register_warranty/',Register_warranty.as_view()),
    path('discount_warranty/',Discount_warranty.as_view()),
    path('warranty_returned/',Warranty_Returned.as_view())
]