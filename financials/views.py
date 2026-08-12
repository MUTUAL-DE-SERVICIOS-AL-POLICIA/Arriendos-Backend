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
from roles.permissions import HasModulePermission
from rest_framework.permissions import IsAuthenticated
from threadlocals.threadlocals import set_thread_variable
from django.shortcuts import get_object_or_404
from Arriendos_Backend import util
from customers import views
from leases.serializer import RentalsSerializer
import logging

logger = logging.getLogger('business')

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
class Register_payment(generics.GenericAPIView):
    serializer_class = Payment_Serializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'financials'
    @swagger_auto_schema(
    operation_description="Lista de pagos por alquiler",
    manual_parameters=[rental],
    )
    def get(self,request):
        set_thread_variable('thread_user', request.user)
        rental_id = request.query_params.get('rental')
        if not rental_id:
            return Response({"error": "Parámetro 'rental' faltante en la consulta."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(self.list_payment(rental_id))
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)
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
            set_thread_variable('thread_user', request.user)
            validated_fields = ["rental", "detail", "mount", "business_name", "nit", "voucher_number"]
            error_message = required_fields(request, validated_fields)
            if error_message:
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
            rental_id = request.data["rental"]
            detail = request.data["detail"]
            mount=request.data["mount"]
            business_name=request.data["business_name"]
            nit=request.data["nit"]
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
                        "business_name":business_name,
                        "nit":nit,
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
                        "business_name":business_name,
                        "nit":nit,
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

    @swagger_auto_schema(
    operation_description="Borrar registro de pago",
    )
    def delete(self,request,rental_id):
        set_thread_variable('thread_user', request.user)
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
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'documents'
    def get(self,request, rental_id):
        return self.Payment_pdf_generate(rental_id)
    def Payment_pdf_generate(self,rental_id):
        payments=Register_payment.list_payment(self,rental_id)["payments"]
        rental= Rental.objects.get(pk=rental_id)
        customer=views.customer_data(rental_id)
        serializer_class = RentalsSerializer
        serializer = serializer_class(rental)
        serialized_rental = serializer.data
        selected_products_data = serialized_rental.get("selected_products")
        params={
            'user': self.request.user,
            'contract_number': rental.contract_number,
            'customer': customer,
            'payments' : payments,
            'selected_products': selected_products_data
        }
        return util.generate_pdf('payments.html',params, filename='canon_de_pagos.pdf')
class Edit_payment(generics.RetrieveUpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = Payment_Serializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'financials'
    def get(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    def patch(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        amount_paid_raw = request.data.get('amount_paid')
        if amount_paid_raw is None:
            return Response({"error": "amount_paid es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount_paid = float(amount_paid_raw)
        except (ValueError, TypeError):
            return Response({"error": "amount_paid debe ser numérico"}, status=status.HTTP_400_BAD_REQUEST)
        list_payment=self.queryset.filter(rental=instance.rental).order_by('id')
        number_payment=list_payment.count()
        if number_payment >1:
            previus_payment=list_payment[len(list_payment)-2]
            previus_payable_mount=float(previus_payment.payable_mount)
            if amount_paid<=previus_payable_mount:
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
class Register_total_payment(generics.GenericAPIView):
    serializer_class = Payment_Serializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'financials'
    @swagger_auto_schema(
    operation_description="Registro del pago total del arriendo",
    request_body=request_body_schema
    )
    def post(self,request):
        set_thread_variable('thread_user', request.user)
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
class Register_warranty(generics.GenericAPIView):
    serializer_class = Warranty_Movement_Serializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'financials'
    @swagger_auto_schema(
    operation_description="Registrar garantía",
    request_body=request_body_schema
    )
    def post(self, request):
        set_thread_variable('thread_user', request.user)
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
        set_thread_variable('thread_user', request.user)
        rental_id = request.query_params.get('rental')
        if not rental_id:
            return Response({"error": "Parámetro 'rental' faltante en la consulta."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            rental=Rental.objects.get(pk=rental_id)
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe."}, status=status.HTTP_404_NOT_FOUND)
        plan=rental.plan
        warranty_mount=0
        if plan is None:
            sp = Selected_Product.objects.filter(rental=rental).first()
            if sp is not None and sp.product and sp.product.room:
                warranty_mount=sp.product.room.warranty
        response_data={
            "state":"success",
            "warranty_movements":self.List_Warranties(rental_id),
            "total_warranty":warranty_mount
        }
        return Response(response_data, status=status.HTTP_200_OK)
    def List_Warranties(self,rental_id):
        warranties=Warranty_Movement.objects.filter(rental=rental_id)
        list_warranties=[]
        n=0
        for warranty in warranties:
            n=n+1
            if warranty.income>0:
                movement_type= "INGRESO"
            elif warranty.discount>0:
                movement_type = "DESCUENTO"
            elif warranty.returned>0:
                movement_type = "RETORNO"
            else:
                movement_type = "MOVIMIENTO"
            warranty_data= {
                "id":warranty.id,
                "correlative":n,
                "type": movement_type,
                "income":warranty.income,
                "discount":warranty.discount,
                "returned":warranty.returned,
                "balance":warranty.balance,
                "detail":warranty.detail,
                "voucher":warranty.voucher_number
            }
            list_warranties.append(warranty_data)
        return list_warranties
    @swagger_auto_schema(
    operation_description="Eliminar el ultimo registro de garantía",
    )
    def delete(self,request,rental_id):
        set_thread_variable('thread_user', request.user)
        try:
            Rental.objects.get(pk=rental_id)
            exist_warranty= Warranty_Movement.objects.filter(rental_id=rental_id).exists()
            if (exist_warranty):
                last_warranty = Warranty_Movement.objects.filter(rental_id=rental_id).latest('id')
                if last_warranty.discount >0:
                    try:
                        event_damage = Event_Damage.objects.filter(warranty_movement=last_warranty).latest('id')
                        event_damage.delete()
                    except Event_Damage.DoesNotExist:
                        pass
                last_warranty.delete()
                return Response({'mensaje': 'Registro eliminado exitosamente'})
            else:
                return Response({"error": "No existen garantías registradas para ese alquiler"}, status=status.HTTP_400_BAD_REQUEST)
        except Rental.DoesNotExist:
            return Response({"error": "El Arriendo no existe."}, status=status.HTTP_404_NOT_FOUND)

rental = openapi.Parameter('rental', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
class Print_Warranties(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'documents'
    def get(self,request,rental_id):
        return self.Warranties_pdf_generate(rental_id)
    def Warranties_pdf_generate(self,rental_id):
        warranties=Register_warranty.List_Warranties(self,rental_id)
        rental= Rental.objects.get(pk=rental_id)
        customer=views.customer_data(rental_id)
        serializer_class = RentalsSerializer
        serializer = serializer_class(rental)
        serialized_rental = serializer.data
        selected_products_data = serialized_rental.get("selected_products")
        params={
            'user': self.request.user,
            'contract_number': rental.contract_number,
            'customer': customer,
            'warranties' : warranties,
            'selected_products':selected_products_data
        }
        return util.generate_pdf('warranties.html',params, filename='registro_de_garantias.pdf')
class Edit_warranty(generics.RetrieveUpdateAPIView):
    queryset = Warranty_Movement.objects.all()
    serializer_class = Warranty_Movement_Serializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'financials'
    def get(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    def patch(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
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
            request.data["balance"]=income_value if income_value is not None else 0
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = {
            "state": "success",
            "message": "El movimiento de Garantía se ha editado exitosamente"
        }
        return Response(response_data)
class Warranty_Return_Request(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'documents'
    @swagger_auto_schema(
    operation_description="Solicitud de devolución de garantía",
    manual_parameters=[rental],
    )
    def get(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        rental = request.GET.get('rental', None)
        if rental is None:
            return Response({"error": "No se ha enviado rental"}, status=status.HTTP_404_NOT_FOUND)
        try:
            warranty=Warranty_Movement.objects.filter(rental_id=rental).latest('id')
        except Warranty_Movement.DoesNotExist:
            return Response({"error": "No hay garantías registradas del alquiler"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            rental_obj = Rental.objects.get(pk=rental)
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe"}, status=status.HTTP_404_NOT_FOUND)
        if not rental_obj.warranty_return_request:
            rental_obj.warranty_return_request = timezone.localtime(timezone.now())
            rental_obj.save()
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
class Discount_warranty(generics.GenericAPIView):
    serializer_class = Warranty_Movement_Serializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'financials'
    rbac_export = True
    @swagger_auto_schema(
    operation_description="API para registro de descuentos por daños",
    request_body=request_body_schema
    )
    def post(self, request):
        set_thread_variable('thread_user', request.user)
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
            rental_state = rental.state_id
            if rental_state == 4:
                return Response({"error": "Ya se ha retornado la garantía"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                selected_product = Selected_Product.objects.get(rental_id = rental_id, pk = product)
            except Selected_Product.DoesNotExist:
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
                new_warranty = Warranty_Movement.objects.latest('id')
                event_damaged_data= {
                    "mount": discount,
                    "selected_product": product,
                    "warranty_movement":new_warranty.id
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
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'financials'
    @swagger_auto_schema(
    operation_description="API de devolución de garantía",
    request_body=request_body_schema
    )
    def post(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
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
                except (ValueError, KeyError):
                    return Response({"error": "Formato de fecha inválido. Use YYYY-MM-DDTHH:MM:SS.sssZ"}, status=status.HTTP_400_BAD_REQUEST)

                
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
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'documents'
    @swagger_auto_schema(
    operation_description="Formulario de conformidad de devolución de garantía",
    manual_parameters=[rental],
    )
    def get(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        rental_param = request.GET.get('rental')
        if rental_param is None:
            return Response({"error": "No se ha enviado rental"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            rental = int(rental_param)
        except (ValueError, TypeError):
            return Response({"error": "El parámetro 'rental' debe ser un número"}, status=status.HTTP_400_BAD_REQUEST)
        warranty= Warranty_Movement.objects.filter(rental_id=rental)
        if Warranty_Movement.objects.filter(rental_id=rental).exists():
            warranty_balance=warranty.latest('id').balance
        else:
            return Response({"error":"El alquiler no tiene garantías registradas"}, status=status.HTTP_404_NOT_FOUND)
        try:
            rental_state_obj = Rental.objects.get(pk=rental)
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe"}, status=status.HTTP_404_NOT_FOUND)
        return Make_Return_Warranty_Form(request, rental)

rental_param = openapi.Parameter('rental', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
product_param = openapi.Parameter('product', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
class Print_Damage_Warranty_Form(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'documents'
    @swagger_auto_schema(
    operation_description="Reimpresión del formulario de ejecución de garantía",
    manual_parameters=[rental_param, product_param],
    )
    def get(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        rental_param_val = request.GET.get('rental')
        product_param_val = request.GET.get('product')
        if rental_param_val is None or product_param_val is None:
            return Response({"error": "Se requieren los parámetros 'rental' y 'product'"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            rental_id = int(rental_param_val)
            product_id = int(product_param_val)
        except (ValueError, TypeError):
            return Response({"error": "Los parámetros 'rental' y 'product' deben ser números"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Rental.objects.get(pk=rental_id)
        except Rental.DoesNotExist:
            return Response({"error": "El alquiler no existe"}, status=status.HTTP_404_NOT_FOUND)
        if not Event_Damage.objects.filter(selected_product_id=product_id).exists():
            return Response({"error": "No hay ejecuciones de garantía para este producto"}, status=status.HTTP_404_NOT_FOUND)
        return Make_Damage_Warranty_Form(request, rental_id, product_id)
