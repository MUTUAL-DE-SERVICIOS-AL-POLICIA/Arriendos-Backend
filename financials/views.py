from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from financials.models import Payment, Warranty_Movement, Event_Damage
from financials.serializer import Payment_Serializer, Warranty_Movement_Serializer, Event_Damage_Serializer
from leases.models import Rental, Selected_Product
from datetime import datetime
from django.utils import timezone
import pytz
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from Arriendos_Backend.util import required_fields
from .function import Make_Damage_Warranty_Form, Make_Warranty_Form, Make_Return_Warranty_Form
from .permissions import *
from rest_framework.permissions import IsAuthenticated
from threadlocals.threadlocals import set_thread_variable
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from Arriendos_Backend import util
from customers import views

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
        return Response(self.list_payment(rental_id))
    def list_payment(self,rental_id):
        total_mount=Rental.objects.get(pk=rental_id).initial_total
        payment = Payment.objects.filter(rental_id=rental_id).order_by("id")
        if payment.exists():
            payable_mount = payment.latest('id').payable_mount
            payment_serialized = self.serializer_class(payment, many=True)
            response_data= {
                "state" :"success",
                "total_mount": total_mount,
                "payable_mount":payable_mount,
                "payments":payment_serialized.data
            }
            return response_data
        else:
            response_data= {
                "state" :"success",
                "total_mount": total_mount,
                "payable_mount":0,
                "payments":[]
            }
        return response_data

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
class Print_payment(generics.ListAPIView):
    serializer_class = Payment_Serializer
    def get(self,request, rental_id):
        return self.Payment_pdf_generate(rental_id)
    def Payment_pdf_generate(self,rental_id):
        payments=Register_payment.list_payment(self,rental_id)["payments"]
        rental= Rental.objects.get(pk=rental_id)
        customer=views.customer_data(rental_id)
        params={
            'user': self.request.user,
            'contract_number': rental.contract_number,
            'customer': customer,
            'payments' : payments
        }
        return util.generate_pdf('payments.html',params)
class Edit_payment(generics.RetrieveUpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = Payment_Serializer
    permission_classes = [IsAuthenticated,HasChangePaymentPermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewPaymentPermission() ]
        if self.request.method == 'PATCH':
            return [HasChangePaymentPermission() ]
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        amount_paid = float(request.data.get('amount_paid'))
        list_payment=self.queryset.filter(rental=instance.rental).order_by('id')
        number_payment=list_payment.count()
        if number_payment >1:
            previus_payment=list_payment[len(list_payment)-2]
            previus_payable_mount=float(previus_payment.payable_mount)
            if amount_paid is not None and amount_paid<=previus_payable_mount:
                request.data["payable_mount"]=float(previus_payment.payable_mount)-float(request.data["amount_paid"])
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                response_data = {
                        "state":"success",
                        "message":"El pago se ha editado exitosamente"
                        }
                return Response(response_data)
            else:
                response_data = {
                "state":"error",
                "error":"El monto registrado es mayor al monto a pagar"
                }
                return Response(response_data,status=status.HTTP_400_BAD_REQUEST)
        else:
            payable_mount = float(instance.rental.initial_total)-amount_paid
            if payable_mount<0:
                return Response({"error": "El monto de pago es mayor al del monto total."}, status=status.HTTP_400_BAD_REQUEST)
            request.data["payable_mount"]=payable_mount
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            response_data = {
                    "state":"success",
                    "message":"El pago se ha editado exitosamente"
                    }
            return Response(response_data)
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
        rental=Rental.objects.get(pk=rental_id)
        plan=rental.plan
        if plan is None:
            warranty_mount=Selected_Product.objects.filter(rental=rental).first().product.room.warranty
        else:
            warranty_mount=0
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
                "id":warranty.id,
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
        response_data={
            "state":"success",
            "warranty_movements":list_warranties,
            "total_warranty":warranty_mount
        }
        return Response(response_data, status=status.HTTP_200_OK)
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
class Edit_warranty(generics.UpdateAPIView):
    queryset = Warranty_Movement.objects.all()
    serializer_class = Warranty_Movement_Serializer
    permission_classes = [IsAuthenticated,HasChangeWarrantyMovementPermission,HasViewWarrantyMovementPermission]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [HasViewWarrantyMovementPermission() ]
        if self.request.method == 'PATCH':
            return [HasChangeWarrantyMovementPermission() ]
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        discount_value = request.data.get('discount')
        income_value = request.data.get('income')
        list_warranty=self.queryset.filter(rental=instance.rental).order_by('id')
        number_rental_warranty=list_warranty.count()
        if number_rental_warranty >1:
            previus_warranty=list_warranty[len(list_warranty)-2]
            if discount_value is not None:
                request.data["balance"]=float(previus_warranty.balance) - float(request.data["discount"])
            if income_value is not None:
                request.data["balance"]=float(previus_warranty.balance) + float(request.data["income"])
        else:
            request.data["balance"]=request.data["income"]
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = {
            "state": "success",
            "message": "El movimiento de Garantía se ha editado exitosamente"
        }
        return Response(response_data)
class Warranty_Return_Request(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
    operation_description="Solicitud de devolución de garantía",
    manual_parameters=[rental],
    )
    def get(self, request, *args, **kwargs):
        rental = request.GET.get('rental', None)
        if rental is None:
            return Response({"error": "No se ha enviado rental"}, status=status.HTTP_404_NOT_FOUND)
        try:
            warranty=Warranty_Movement.objects.filter(rental_id=rental).latest('id')
        except:
            return Response({"error": "No hay garantías registradas del alquiler"}, status=status.HTTP_400_BAD_REQUEST)
        rental_state = Rental.objects.get(pk=rental)
        rental_state = rental_state.state_id
        if rental_state == 4:
            return Response({"error": "Ya se ha retornado la garantía"}, status=status.HTTP_404_NOT_FOUND)
        now = timezone.localtime(timezone.now())
        rental_date=Rental.objects.get(pk=rental)
        rental_date.warranty_return_request = now
        rental_date.save()
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
        set_thread_variable('thread_user', self.request.user)
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
            try:
                rental_id = request.data["rental"]
                product = request.data["product"]
                rental_state = Rental.objects.get(pk=rental_id)
                rental_state = rental_state.state_id
                if rental_state == 4:
                    return Response({"error": "Ya se ha retornado la garantía"}, status=status.HTTP_404_NOT_FOUND)
                if rental_id is None and product is None:
                    return Response(error_message, status=400)
                return Make_Damage_Warranty_Form(request, rental_id, product)
            except:
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
                return Make_Damage_Warranty_Form(request, rental_id, product)
            else:
                return Response({"error":"no tiene garantias registrada"}, status=status.HTTP_400_BAD_REQUEST)
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'rental': openapi.Schema(type=openapi.TYPE_INTEGER),
        'return_date': openapi.Schema(type=openapi.TYPE_STRING),
    }
)
class Warranty_Returned(generics.GenericAPIView):
    serializer_class = Warranty_Movement_Serializer
    permission_classes = [IsAuthenticated, HasAddWarrantyMovementPermission]
    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        if self.request.method == 'POST':
            return [HasAddWarrantyMovementPermission()]
    @swagger_auto_schema(
    operation_description="API de devolución de garantía",
    request_body=request_body_schema
    )
    def post(self, request, *args, **kwargs):
        validated_fields = ["rental", "return_date"]
        error_message = required_fields(request, validated_fields)
        rental_id = request.data.get("rental")
        if error_message:
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            rental = Rental.objects.get(pk=rental_id)
            warranty= Warranty_Movement.objects.filter(rental_id=rental.id)
            if (warranty.exists()):
                warranty_balance=warranty.latest('id').balance
                if warranty_balance == 0:
                    return Response({"error":f"no se puede devolver la garatía, porque el monto de la garantía es: {warranty_balance}"}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    return_date_str = request.data["return_date"]
                    return_date = datetime.strptime(return_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    return_date = pytz.timezone('America/La_Paz').localize(return_date)
                except ValueError:
                    return HttpResponseBadRequest("Error de formato de la fecha")

                
                rental_date = get_object_or_404(Rental, pk=rental_id)

                rental_date.warranty_returned = str(return_date)
                rental_date.save()
                
                
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
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
    operation_description="Formulario de conformidad de devolución de garantía",
    manual_parameters=[rental],
    )
    def get(self, request, *args, **kwargs):
        rental = int(request.GET.get('rental', None))
        warranty= Warranty_Movement.objects.filter(rental_id=rental)
        if rental is None:
            return Response({"error": "No se ha enviado rental"}, status=status.HTTP_404_NOT_FOUND)
        if Warranty_Movement.objects.filter(rental_id=rental).exists():
            warranty_balance=warranty.latest('id').balance
        else:
            return Response({"error":"El alquiler no tiene garantías registradas"}, status=status.HTTP_404_NOT_FOUND)
        rental_state = Rental.objects.get(pk=rental)
        rental_state = rental_state.state_id
        if rental_state == 4:
            return Response({"error": "Ya se ha retornado la garantía"}, status=status.HTTP_404_NOT_FOUND)
        #if warranty_balance == 0:
        #    return Response({"error":f"La garantía actual es: {warranty_balance}"}, status=status.HTTP_404_NOT_FOUND)
        return Make_Return_Warranty_Form(request, rental)