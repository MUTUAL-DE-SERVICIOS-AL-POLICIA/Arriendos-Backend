from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from financials.models import Payment, Warranty_Movement, Event_Damage
from financials.serializer import Payment_Serializer, Warranty_Movement_Serializer, Event_Damage_Serializer
from leases.models import Rental, Selected_Product
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from Arriendos_Backend.util import required_fields
from .function import Make_Damage_Warranty_Form, Make_Warranty_Form, Make_Return_Warranty_Form
from .permissions import *
from rest_framework.permissions import IsAuthenticated
from threadlocals.threadlocals import set_thread_variable

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'rental': openapi.Schema(type=openapi.TYPE_INTEGER),
        'mount': openapi.Schema(type=openapi.TYPE_INTEGER),
        'voucher_number': openapi.Schema(type=openapi.TYPE_STRING),
        'detail': openapi.Schema(type=openapi.TYPE_STRING)
    }
)
rental = openapi.Parameter('rental', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
class Register_payment(generics.ListAPIView):
    serializer_class = Payment_Serializer
    permission_classes = [IsAuthenticated, HasAddPaymentPermission, HasViewPaymentPermission,HasDeletePaymentPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'POST':
            return [HasAddPaymentPermission()]
        if self.request.method == 'GET':
            return [HasViewPaymentPermission()]
        if self.request.method == 'DELETE':
            return [HasDeletePaymentPermission()]
    @swagger_auto_schema(
    operation_description="Lista de pagos por alquiler",
    manual_parameters=[rental],
    )
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
            response_data= {
                "state" :"success",
                "total_mount": total_mount,
                "payable_mount":0,
                "payments":[]
            }
            return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
    operation_description="Registro de pagos",
    request_body=request_body_schema
    )
    def post(self,request):
            rental_id = request.data["rental"]
            detail = request.data["detail"]
            mount=request.data["mount"]
            voucher = request.data["voucher_number"]
            if mount<=0:
                return Response({"error":"el monto ingresado debe ser mayor 0"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                rental = Rental.objects.get(pk=rental_id)
                exist_payment= Payment.objects.filter(rental_id=rental_id).exists()
                if (exist_payment):
                    last_payment = Payment.objects.filter(rental_id=rental_id).latest('id')
                    total =float(last_payment.payable_mount)-mount
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
                    total =float(rental.initial_total)-mount
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
                return Response({"error": "El alquiler no existe."}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
    operation_description="Borrar registro de pago",
    )
    def delete(self,request,rental_id):
        try:
            exist_payment= Payment.objects.filter(rental_id=rental_id).exists()
            if (exist_payment):
                last_payment = Payment.objects.filter(rental_id=rental_id).latest('id')
                last_payment.delete()
                return Response({'mensaje': 'Registro eliminado exitosamente'})
            else:
                return Response({"error": "No existen pagos para ese alquiler"}, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({"error": "El pago no existe."}, status=status.HTTP_400_BAD_REQUEST)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'rental': openapi.Schema(type=openapi.TYPE_INTEGER),
        'mount': openapi.Schema(type=openapi.TYPE_INTEGER),
        'voucher_number': openapi.Schema(type=openapi.TYPE_STRING),
        'detail': openapi.Schema(type=openapi.TYPE_STRING)
    }
)
class Register_total_payment(generics.ListAPIView):
    serializer_class = Payment_Serializer
    permission_classes = [IsAuthenticated, HasAddPaymentPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'POST':
            return [HasAddPaymentPermission()]
    @swagger_auto_schema(
    operation_description="Registro del pago total del arriendo",
    request_body=request_body_schema
    )
    def post(self,request):
        rental_id = request.data["rental"]
        detail = request.data["detail"]
        voucher = request.data["voucher_number"]
        try:
            rental = Rental.objects.get(pk=rental_id)
            exist_payment= Payment.objects.filter(rental_id=rental_id).exists()
            if (exist_payment):
                last_payment = Payment.objects.filter(rental_id=rental_id).latest('id')
                mount=last_payment.payable_mount
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
                mount= rental.initial_total
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
rental = openapi.Parameter('rental', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'rental': openapi.Schema(type=openapi.TYPE_INTEGER),
        'income': openapi.Schema(type=openapi.TYPE_INTEGER),
        'voucher_number': openapi.Schema(type=openapi.TYPE_STRING),
        'detail': openapi.Schema(type=openapi.TYPE_STRING)
    }
)
class Register_warranty(generics.ListAPIView):
    serializer_class = Warranty_Movement_Serializer
    permission_classes = [IsAuthenticated, HasAddWarrantyMovementPermission, HasViewWarrantyMovementPermission,HasDeleteWarrantyMovementPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'POST':
            return [HasAddWarrantyMovementPermission()]
        if self.request.method == 'GET':
            return [HasViewWarrantyMovementPermission()]
        if self.request.method == 'DELETE':
            return [HasDeleteWarrantyMovementPermission()]
    @swagger_auto_schema(
    operation_description="Registrar garantía",
    request_body=request_body_schema
    )
    def post(self, request):
        validated_fields = ["rental","income", "detail","voucher_number"]
        error_message = required_fields(request, validated_fields)
        if error_message:
            return Response(error_message, status=400)
        rental_id = request.data["rental"]
        income = request.data["income"]
        detail = request.data["detail"]
        voucher = request.data["voucher_number"]
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
                    "voucher_number":voucher
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
                    "voucher_number":voucher
                }
                serializer = self.serializer_class(data=warranty_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response({"message": "La garantía se ha registrado exitosamente"}, status=status.HTTP_201_CREATED)
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema(
    operation_description="Listado de garantías por alquiler",
    manual_parameters=[rental],
    )
    def get(self,request):
        rental_id = request.query_params.get('rental')
        if not rental_id:
            return Response({"error": "Parámetro 'rental' faltante en la consulta."}, status=status.HTTP_400_BAD_REQUEST)
        warranties=Warranty_Movement.objects.filter(rental=rental_id)
        list_warranties=[]
        n=0
        for warranty in warranties:
            n=n+1
            if warranty.income>0:
                type= "INGRESO"
            if warranty.discount>0:
                type = "DESCUENTO"
            if warranty.returned>0:
                type = "RETORNO"
            response_data= {
                "correlative":n,
                "type": type,
                "income":warranty.income,
                "discount":warranty.discount,
                "returned":warranty.returned,
                "balance":warranty.balance,
                "detail":warranty.detail,
                "voucher":warranty.voucher_number
            }
            list_warranties.append(response_data)
        return Response(list_warranties, status=status.HTTP_200_OK)
    @swagger_auto_schema(
    operation_description="Eliminar el ultimo registro de garantía",
    )
    def delete(self,request,rental_id):
        try:
            Rental.objects.get(pk=rental_id)
            exist_warranty= Warranty_Movement.objects.filter(rental_id=rental_id).exists()
            if (exist_warranty):
                last_warranty = Warranty_Movement.objects.filter(rental_id=rental_id).latest('id')
                if last_warranty.discount >0:
                    event_damage = Event_Damage.objects.filter(warranty_movement=last_warranty).latest('id')
                    event_damage.delete()
                last_warranty.delete()
                return Response({'mensaje': 'Registro eliminado exitosamente'})
            else:
                return Response({"error": "No existen garantías registradas para ese alquiler"}, status=status.HTTP_400_BAD_REQUEST)
        except Rental.DoesNotExist:
            return Response({"error": "El Arriendo no existe."}, status=status.HTTP_400_BAD_REQUEST)

rental = openapi.Parameter('rental', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

class Warranty_Return_Request(generics.GenericAPIView):
    @swagger_auto_schema(
    operation_description="Solicitud de devolución de garantía",
    manual_parameters=[rental],
    )
    def get(self, request, *args, **kwargs):
        rental = request.GET.get('rental', None)
        if rental is None:
            return Response({"error": "No se ha enviado rental"}, status=status.HTTP_404_NOT_FOUND)
        return Make_Warranty_Form(request, rental)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'detail': openapi.Schema(type=openapi.TYPE_STRING),
        'rental': openapi.Schema(type=openapi.TYPE_INTEGER),
        'discount': openapi.Schema(type=openapi.TYPE_INTEGER),
        'product': openapi.Schema(type=openapi.TYPE_INTEGER)
    }
)
class Discount_warranty(generics.ListAPIView):
    serializer_class = Warranty_Movement_Serializer
    permission_classes = [IsAuthenticated, HasAddWarrantyMovementPermission]
    def get_permissions(self):
        if self.request.method == 'POST':
            return [HasAddWarrantyMovementPermission()]
    @swagger_auto_schema(
    operation_description="API para registro de descuentos por daños",
    request_body=request_body_schema
    )
    def post(self, request):
        validated_fields = ["rental","product", "detail","discount"]
        error_message = required_fields(request, validated_fields)
        if error_message:
            return Response(error_message, status=400)
        rental_id = request.data["rental"]
        product = request.data["product"]
        detail = request.data["detail"]
        discount = request.data["discount"]
        if discount<=0:
            return Response({"error":"el monto ingresado es 0 no se registra el descuento"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            rental = Rental.objects.get(pk=rental_id)
            try:
                selected_product = Selected_Product.objects.get(rental_id = rental_id, pk = product)
                if selected_product is None:
                    return Response({'error': 'No se ha podido obtener el producto'}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'error': 'No se encuentra el producto relacionado al arriendo'}, status=status.HTTP_400_BAD_REQUEST)
            warranty= Warranty_Movement.objects.filter(rental_id=rental.id)
            if (warranty.exists()):
                if warranty.latest('id').balance <discount:
                   return Response({"error":"el monto ingresado mayor al del saldo"}, status=status.HTTP_400_BAD_REQUEST)
                warranty_balance=warranty.latest('id').balance
                total=  warranty_balance - discount
                warranty_data = {
                    "rental": rental_id,
                    "income": 0,
                    "discount": discount,
                    "returned": 0,
                    "balance": total,
                    "detail": detail,
                    "voucher_number":0
                }
                serializer = self.serializer_class(data=warranty_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                last_warranty= warranty.latest('id').id
                event_damaged_data= {
                    "mount": discount,
                    "selected_product": product,
                    "warranty_movement":last_warranty
                }
                event_damaged_serialized = Event_Damage_Serializer(data=event_damaged_data)
                event_damaged_serialized.is_valid(raise_exception=True)
                event_damaged_serialized.save()
                return Make_Damage_Warranty_Form(request, rental_id, product, discount, total, detail)
            else:
                return Response({"error":"no tiene garantias registrada"}, status=status.HTTP_400_BAD_REQUEST)
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'rental': openapi.Schema(type=openapi.TYPE_INTEGER),
    }
)
class Warranty_Returned(generics.ListAPIView):
    serializer_class = Warranty_Movement_Serializer
    permission_classes = [IsAuthenticated, HasAddWarrantyMovementPermission]
    def get_permissions(self):
        if self.request.method == 'POST':
            return [HasAddWarrantyMovementPermission()]
    @swagger_auto_schema(
    operation_description="API de devolución de garantía",
    request_body=request_body_schema
    )
    def post(self, request):
        validated_fields = ["rental"]
        error_message = required_fields(request, validated_fields)
        if error_message:
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        rental_id = request.data["rental"]
        try:
            rental = Rental.objects.get(pk=rental_id)
            warranty= Warranty_Movement.objects.filter(rental_id=rental.id)
            if (warranty.exists()):
                warranty_balance=warranty.latest('id').balance
                if warranty_balance == 0:
                    return Response({"error":f"no se puede devolver la garatía, porque el monto de la garantía es: {warranty_balance}"}, status=status.HTTP_400_BAD_REQUEST)
                total=  0
                returned=warranty_balance
                warranty_data = {
                    "rental": rental_id,
                    "income": 0,
                    "discount": 0,
                    "returned": returned,
                    "balance": total,
                    "voucher_number":0
                }
                serializer = self.serializer_class(data=warranty_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"message": "Se retorno la garantía exitosamente"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error":"no tiene garantias registrada"}, status=status.HTTP_400_BAD_REQUEST)
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)

rental = openapi.Parameter('rental', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
class Return_Warranty_Form(generics.GenericAPIView):

    @swagger_auto_schema(
    operation_description="Formulario de conformidad de devolución de garantía",
    manual_parameters=[rental],
    )
    def get(self, request, *args, **kwargs):
        rental = int(request.GET.get('rental', None))
        if rental is None:
            return Response({"error": "No se ha enviado rental"}, status=status.HTTP_404_NOT_FOUND)
        return Make_Return_Warranty_Form(request, rental)