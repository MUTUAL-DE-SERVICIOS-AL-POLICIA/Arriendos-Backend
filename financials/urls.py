from django.urls import path
from financials.views import Register_payment,Register_warranty,Discount_warranty, Warranty_Returned, Register_total_payment, Warranty_Return_Request, Return_Warranty_Form, Edit_payment, Edit_warranty

urlpatterns = [
    path('register_payment/',Register_payment.as_view()),
    path('register_payment/<int:rental_id>/',Register_payment.as_view()),
    path('edit_payment/<int:pk>/', Edit_payment.as_view(), name='payment-patch'),
    path("register_total_payment/", Register_total_payment.as_view()),
    path('register_warranty/',Register_warranty.as_view()),
    path("register_warranty/<int:rental_id>/", Register_warranty.as_view()),
    path('edit_warranty/<int:pk>/', Edit_warranty.as_view(), name='warranty-patch'),
    path('discount_warranty/',Discount_warranty.as_view()),
    path('warranty_returned/',Warranty_Returned.as_view()),
    path('warranty_request/', Warranty_Return_Request.as_view()),
    path('return_warranty_form/', Return_Warranty_Form.as_view())
]