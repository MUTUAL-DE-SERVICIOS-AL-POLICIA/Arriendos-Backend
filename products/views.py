"""
Vistas API para la gestión de productos e historial de precios.

Este módulo contiene las vistas para gestionar:
- Tarifas (Rate)
- Rangos de Horas (HourRange)
- Productos (Product)
- Precios e Historial de Precios (Price)
- Precios por Hora Adicional
- Productos posibles para un tipo de cliente

Todas las vistas utilizan HasModulePermission para validar
que el usuario tenga los permisos necesarios sobre el módulo 'products'.

Historial de Precios:
- GET /product/price_history/?product=<id>: Obtiene historial de precios
- Al crear producto: Se crea precio inicial con valid_from=now
- Al actualizar precio: Se desactiva el anterior y se crea uno nuevo

Autor: Dilan Torrez
Fecha: 2026
"""

from rest_framework import generics, status
from rest_framework.views import APIView
from .models import Rate, HourRange, Product, Price, Price_Additional_Hour
from customers.models import Customer_type
from .serializers import RateSerializer, HourRangeSerializer, ProductsSerializer, ProductSerializer, PriceSerializer, PriceAdditionalHourSerializer, PriceHistorySerializer
from leases.models import Selected_Product
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from threadlocals.threadlocals import set_thread_variable
import math
from requirements.models import RateRequirement
from roles.permissions import HasModulePermission
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone


class Rate_Api(generics.GenericAPIView):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    @swagger_auto_schema(
    operation_description="Lista de Tarifas",
    )
    def get(self, request, *args, **kwargs):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        search_param = request.GET.get('search')
        rates = Rate.objects.all()
        if search_param:
            rates = rates.filter(name__icontains=search_param)
        total_rates = rates.count()
        if limit_num == -1:
            paginated = rates
        else:
            start_num = page_num * limit_num
            end_num = limit_num * (page_num + 1)
            paginated = rates[start_num:end_num]
        serializer = self.serializer_class(paginated, many=True)
        return Response({
            "status": "success",
            "total": total_rates,
            "page": page_num,
            "last_page": math.ceil(total_rates/ limit_num) if limit_num > 0 else 0,
            "rates": serializer.data
        })

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'day': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING)
        ),
        'rate':openapi.Schema(type=openapi.TYPE_INTEGER),
        'room':openapi.Schema(type=openapi.TYPE_INTEGER),
        'hour_range': openapi.Schema(type=openapi.TYPE_INTEGER),
        'mount': openapi.Schema(type=openapi.TYPE_INTEGER)
    }
)
class Product_Api(generics.GenericAPIView):
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    def get_product(self, pk):
        try:
            return Product.objects.get(pk=pk, is_deleted=False)
        except Product.DoesNotExist:
            return None

    @swagger_auto_schema(
    operation_description="Lista de productos y precio",
    )
    def get(self, request, *args, **kwargs):
        queryset = Product.objects.filter(is_deleted=False).select_related(
            'rate', 'room', 'room__property', 'hour_range'
        ).prefetch_related('price_set')
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        total_products = queryset.count()
        if limit_num == -1:
            paginated_products = queryset
        else:
            start_num = page_num * limit_num
            end_num = limit_num * (page_num + 1)
            paginated_products = queryset[start_num:end_num]
        serializer = ProductsSerializer(paginated_products, many=True)
        serialized_data = serializer.data
        for product_data in serialized_data:
            product_id = product_data.get('id')
            product_obj = next((p for p in paginated_products if p.id == product_id), None)
            if product_obj and hasattr(product_obj, '_prefetched_prices'):
                active_price = next((p for p in product_obj._prefetched_prices if p.is_active), None)
                if active_price:
                    product_data['mount'] = active_price.mount

        return Response({
        "status": "success",
        "total": total_products,
        "page": page_num,
        "last_page": math.ceil(total_products/ limit_num) if limit_num > 0 else 0,
        "products": serialized_data
        })

    @swagger_auto_schema(
    operation_description="Crear productos",
    request_body=request_body_schema
    )
    def post(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            Product_saved=serializer.save()
            mount=request.data.get('mount', '')
            price_data = {
                "mount": mount,
                "is_active": True,
                "product": Product_saved.id,
                "valid_from": timezone.now()
            }
            PriceSerialized=PriceSerializer(data=price_data)
            if (PriceSerialized.is_valid()):
                PriceSerialized.save()
                combined_response=[serializer.data, PriceSerialized.data]
                return Response({"status": "success", "data": combined_response}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": "fail", "message": PriceSerialized.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
    operation_description="Actualizar producto y precio",
    request_body=request_body_schema
    )
    def patch(self,request, pk ):
        set_thread_variable('thread_user', request.user)
        product = self.get_product(pk=pk)
        if product == None:
            return Response({"status": "success", "message": f"Product with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        if 'mount' in request.data:
            mount_value = request.data['mount']
            now = timezone.now()
            active_prices = Price.objects.filter(product_id=pk, is_active=True)
            for price in active_prices:
                price.is_active = False
                price.valid_to = now
                price.save()
            new_price={
                "mount":mount_value,
                "is_active":True,
                "product":pk,
                "valid_from": now
            }
            price_serialized=PriceSerializer(data=new_price)
            if price_serialized.is_valid():
                price_serialized.save()
                price_response=price_serialized.data
            product_serialized = ProductSerializer(product, data=request.data, partial=True)
            if product_serialized.is_valid():
                product_serialized.save()
                product_response=product_serialized.data
                combined_response = {
                    'price': price_response,
                    'product': product_response
                }
                return Response({"status": "success", "data": combined_response}, status=status.HTTP_200_OK)
            return Response({"status": "fail", "message": product_serialized.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.serializer_class(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": {"product": serializer.data}}, status=status.HTTP_200_OK)
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_product(pk=pk)
        if product is None:
            return Response({"status": "fail", "message": f"Producto con id {pk} no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        product.is_deleted = True
        product.save()
        return Response({"status": "success", "message": "Producto eliminado correctamente"}, status=status.HTTP_200_OK)

class HourRange_List_Create_View(generics.ListCreateAPIView):
    queryset = HourRange.objects.all()
    serializer_class = HourRangeSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        return [IsAuthenticated(), HasModulePermission()]

class HourRange_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = HourRange.objects.all()
    serializer_class = HourRangeSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        return [IsAuthenticated(), HasModulePermission()]

class Price_List_Create_View(generics.ListCreateAPIView):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        return [IsAuthenticated(), HasModulePermission()]

class Price_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset=Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        return [IsAuthenticated(), HasModulePermission()]

product_param = openapi.Parameter('product', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)


class Price_History_View(generics.GenericAPIView):
    """
    Vista para obtener el historial de precios de un producto.

    Retorna todos los precios registrados para un producto específico,
    ordenados por fecha de creación (más reciente primero).

    Permisos requeridos: products.view (Ver productos)
    Método HTTP: GET

    Parámetros de consulta:
    - product: ID del producto (requerido)

    Estructura de respuesta (200 OK):
    {
        "status": "success",
        "prices": [
            {
                "id": 1,
                "mount": 150.0,
                "is_active": true,
                "valid_from": "2026-01-15T10:00:00Z",
                "valid_to": null,
                "created_at": "2026-01-15T10:00:00Z"
            },
            {
                "id": 2,
                "mount": 120.0,
                "is_active": false,
                "valid_from": "2026-01-01T10:00:00Z",
                "valid_to": "2026-01-15T10:00:00Z",
                "created_at": "2026-01-01T10:00:00Z"
            }
        ]
    }

    Error (400 Bad Request):
    {
        "error": "Parámetro 'product' requerido"
    }

    URL: /api/product/price_history/
    """
    serializer_class = PriceHistorySerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    @swagger_auto_schema(
        operation_description="Historial de precios de un producto",
        manual_parameters=[product_param],
    )
    def get(self, request):
        """Obtiene el historial de precios de un producto específico."""
        product_id = request.query_params.get('product')
        if not product_id:
            return Response({"error": "Parámetro 'product' requerido"}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener precios ordenados por fecha de creación (más reciente primero)
        prices = Price.objects.filter(product_id=product_id).order_by('-created_at')
        serializer = self.serializer_class(prices, many=True)
        return Response({
            "status": "success",
            "prices": serializer.data
        }, status=status.HTTP_200_OK)

class Additional_Hour_List_Create_View(generics.ListCreateAPIView):
    queryset = Price_Additional_Hour.objects.all()
    serializer_class = PriceAdditionalHourSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        return [IsAuthenticated(), HasModulePermission()]

class Additional_Hour_Retrieve_Update_Destroy_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = Price_Additional_Hour.objects.all()
    serializer_class = PriceAdditionalHourSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    def get_permissions(self):
        set_thread_variable('thread_user', self.request.user)
        return [IsAuthenticated(), HasModulePermission()]

selected_product = openapi.Parameter('selected_product', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)

class Get_price_additional_hour(generics.ListAPIView):
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    @swagger_auto_schema(
    operation_description="Precio de hora adicional del producto seleccionado",
    manual_parameters=[selected_product],
    )
    def get(self,request):
        selected_product_id = request.query_params.get('selected_product')
        try:
            selected_product=Selected_Product.objects.get(pk=selected_product_id)
            room = selected_product.product.room.id
            hour = selected_product.product.hour_range.id
            price_additional_hour=Price_Additional_Hour.objects.filter(room=room, hourRange=hour, state=True)
            if price_additional_hour.exists():
                price=price_additional_hour.first().mount
                return Response({"price":price}, status=status.HTTP_200_OK)
            return Response({"error": "No existe hora extra para ese producto"}, status=status.HTTP_404_NOT_FOUND)
        except Selected_Product.DoesNotExist:
            return Response({"error": "No existe el producto seleccionado"}, status=status.HTTP_404_NOT_FOUND)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'customer_type': openapi.Schema(type=openapi.TYPE_INTEGER),
        'room_id': openapi.Schema(type=openapi.TYPE_INTEGER)
    }
)
class Posible_product(APIView):
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    @swagger_auto_schema(
    request_body=request_body_schema,
    )
    def post(self, request):
        set_thread_variable('thread_user', request.user)
        customer_type_id = request.data.get('customer_type')
        room_id=request.data.get('room_id')
        try:
            rate_requirement = RateRequirement.objects.filter(customer_type_id=customer_type_id).first()
            if rate_requirement:
                rate_id = rate_requirement.rate.id
                products_with_rate = Product.objects.filter(
                    rate=rate_id, room=room_id, is_deleted=False
                ).select_related(
                    'rate', 'room', 'room__property', 'hour_range'
                ).prefetch_related('price_set')
                serializer = ProductsSerializer(products_with_rate, many=True)
                return Response({'status': 'success', 'products': serializer.data})
            else:
                customer=Customer_type.objects.get(pk=customer_type_id)
                return Response({"error": f"No hay requisitos asociados a la tarifa perteneciente al tipo de cliente: {customer.name}"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer_type.DoesNotExist:
            return Response({"error": "Tipo de cliente no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

class Product_Filter_Options(generics.GenericAPIView):
    """Endpoint para obtener las opciones de filtro (tarifas, inmuebles, rangos de horas, días)"""
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    def get(self, request):
        from rooms.models import Room, Property
        rates = list(Rate.objects.values('id', 'name'))
        properties = list(Property.objects.values('id', 'name'))
        rooms = list(Room.objects.filter(is_active=True).values('id', 'name', 'property_id'))
        hour_ranges = list(HourRange.objects.values('id', 'time'))
        # Días disponibles (extraídos de la BD)
        all_days = set()
        for d in Product.objects.values_list('day', flat=True):
            all_days.update(d)
        days = sorted(all_days)
        return Response({
            "status": "success",
            "rates": rates,
            "properties": properties,
            "rooms": rooms,
            "hour_ranges": hour_ranges,
            "days": days
        })


class Product_Filter(generics.ListAPIView):
    serializer_class = ProductsSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'products'

    def get_queryset(self):
        try:
            # Búsqueda por texto
            query_param = self.request.query_params.get('search', '')
            # Filtros por columna
            rate_id = self.request.query_params.get('rate_id', '')
            property_id = self.request.query_params.get('property_id', '')
            room_id = self.request.query_params.get('room_id', '')
            hour_range_id = self.request.query_params.get('hour_range_id', '')
            day = self.request.query_params.get('day', '')

            queryset = Product.objects.filter(is_deleted=False).select_related(
                'rate', 'room', 'room__property', 'hour_range'
            ).prefetch_related('price_set')

            # Aplicar búsqueda por texto
            if query_param:
                queryset = queryset.filter(
                    Q(id__icontains=query_param) |
                    Q(rate_id__name__icontains=query_param) |
                    Q(room_id__name__icontains=query_param) |
                    Q(room_id__property__name__icontains=query_param)
                )

            # Aplicar filtro por tarifa
            if rate_id:
                queryset = queryset.filter(rate_id=rate_id)

            # Aplicar filtro por inmueble
            if property_id:
                queryset = queryset.filter(room_id__property_id=property_id)

            # Aplicar filtro por ambiente
            if room_id:
                queryset = queryset.filter(room_id=room_id)

            # Aplicar filtro por rango de horas
            if hour_range_id:
                queryset = queryset.filter(hour_range_id=hour_range_id)

            # Aplicar filtro por día (el campo day es un array, case-insensitive)
            if day:
                # Convertir a mayúsculas para coincidir con la BD
                days = [d.strip().upper() for d in day.split(',') if d.strip()]
                queryset = queryset.filter(day__overlap=days)

            return queryset
        except ValueError:
            return Product.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page_num = int(request.GET.get('page', 0))
            limit_num = int(request.GET.get('limit', 10))
            total_products = queryset.count()
            
            # Si limit es -1, mostrar todos
            if limit_num == -1:
                paginated_products = queryset
            else:
                # Paginar ANTES de serializar
                start_num = page_num * limit_num
                end_num = limit_num * (page_num + 1)
                paginated_products = queryset[start_num:end_num]
            
            # Serializar solo los productos paginados
            serializer = ProductsSerializer(paginated_products, many=True)
            serialized_data = serializer.data
            
            # Obtener precios activos de forma optimizada (una sola query)
            product_ids = [p.get('id') for p in serialized_data]
            active_prices = Price.objects.filter(
                product_id__in=product_ids, is_active=True
            ).values('product_id', 'mount')
            price_map = {p['product_id']: p['mount'] for p in active_prices}
            
            for product_data in serialized_data:
                product_id = product_data.get('id')
                mount = price_map.get(product_id)
                if mount is not None:
                    product_data['mount'] = mount
            
            response_data = {
                "status": "success",
                "total": total_products,
                "page": page_num,
                "last_page": math.ceil(total_products / limit_num) if limit_num > 0 else 0,
                "products": serialized_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
