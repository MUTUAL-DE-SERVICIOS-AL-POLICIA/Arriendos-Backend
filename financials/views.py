from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from financials.models import Payment, Warranty_Movement
from financials.serializer import Payment_Serializer, Warranty_Movement_Serializer
from leases.models import Rental
from Arriendos_Backend.util import required_fields
# Create your views here.
class Register_payment(generics.ListAPIView):
    serializer_class = Payment_Serializer
    def get(self,request):
        rental_id = request.query_params.get('rental')
        if not rental_id:
            return Response({"error": "Parámetro 'rental' faltante en la consulta."}, status=status.HTTP_400_BAD_REQUEST)
        total_mount=Rental.objects.get(pk=rental_id).initial_total
        payment = Payment.objects.filter(rental_id=rental_id)
        if payment.exists():
            payable_mount = payment.latest('id').payable_mount
            payment_serialized = self.serializer_class(payment, many=True)
            response_data= {
                "state" :"success",
                "total_mount": total_mount,
                "payable_mount":payable_mount,
                "payments":payment_serialized.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "El alquiler no tiene pagos registrados."}, status=status.HTTP_404_NOT_FOUND)
    def post(self,request):
            rental_id = request.data["rental"]
            detail = request.data["detail"]
            mount=request.data["mount"]
            voucher = request.data["voucher_number"]
            try:
                rental = Rental.objects.get(pk=rental_id)
                exist_payment= Payment.objects.filter(rental_id=rental_id).exists()
                if (exist_payment):
                    last_payment = Payment.objects.filter(rental_id=rental_id).latest('id')
                    total =last_payment.payable_mount-mount
                    if total<0:
                        return Response({"error": "El monto de pago es mayor al del monto total."}, status=status.HTTP_400_BAD_REQUEST)
                    payment_data={
                        "rental": rental_id,
                        "detail": detail,
                        "payable_mount": total,
                        "amount_paid": mount,
                        "voucher_number":voucher
                    }
                    serializer = self.get_serializer(data=payment_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    response_data = {
                    "state":"success",
                    "message":"El pago se ha registrado exitosamente"
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    total =rental.initial_total-mount
                    if total<0:
                        return Response({"error": "El monto de pago es mayor al del monto total."}, status=status.HTTP_400_BAD_REQUEST)
                    payment_data={
                        "rental": rental_id,
                        "detail": detail,
                        "payable_mount": total,
                        "amount_paid": mount,
                        "voucher_number":voucher
                    }
                    serializer = self.get_serializer(data=payment_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    response_data = {
                    "state":"success",
                    "message":"El pago se ha registrado exitosamente"
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
            except Rental.DoesNotExist:
                return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)
class Register_warranty(generics.ListAPIView):
    serializer_class = Warranty_Movement_Serializer
    def post(self, request):
        validated_fields = ["rental","income", "detail"]
        error_message = required_fields(request, validated_fields)
        if error_message:
            return Response(error_message, status=400)
        rental_id = request.data["rental"]
        income = request.data["income"]
        detail = request.data["detail"]
        if income<=0:
            return Response({"error":"el monto ingresado es 0"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            rental = Rental.objects.get(pk=rental_id)
            warranty= Warranty_Movement.objects.filter(rental_id=rental.id)
            if (warranty.exists()):
                warranty_balance=warranty.latest('id').balance
                total= + income + warranty_balance
                warranty_data = {
                    "rental": rental_id,
                    "income": income,
                    "discount": 0,
                    "returned": 0,
                    "balance": total,
                    "detail": detail,
                }
                serializer = self.serializer_class(data=warranty_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"message": "La garantía se ha registrado exitosamente"}, status=status.HTTP_201_CREATED)
            else:
                warranty_data = {
                    "rental": rental_id,
                    "income": income,
                    "discount": 0,
                    "returned": 0,
                    "balance": income,
                    "detail": detail,
                }
                serializer = self.serializer_class(data=warranty_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response({"message": "La garantía se ha registrado exitosamente"}, status=status.HTTP_201_CREATED)
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)