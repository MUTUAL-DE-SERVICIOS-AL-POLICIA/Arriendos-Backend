"""
Vistas para la app de registros (auditoria interna).

Endpoints:
- GET /api/records/ - Lista paginada de registros de auditoria
- GET /api/records/available_by_rental/ - Documentos disponibles por alquiler

Autor: Dilan Torrez
Fecha: 2026
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from roles.permissions import HasModulePermission
from users.models import Record
from .serializers import RecordSerializer


class Records_View(generics.ListAPIView):
    """
    Vista para consultar registros de auditoria del sistema.

    Permite filtrar por:
    - user: ID del usuario
    - action: tipo de accion (create, update, delete)
    - model: nombre del modelo
    - start_date: fecha inicio (YYYY-MM-DD)
    - end_date: fecha fin (YYYY-MM-DD)
    - search: busqueda en detalle
    """
    serializer_class = RecordSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'records'

    def get_queryset(self):
        queryset = Record.objects.all().select_related('user')

        user_id = self.request.query_params.get('user', '')
        action = self.request.query_params.get('action', '')
        model = self.request.query_params.get('model', '')
        start_date = self.request.query_params.get('start_date', '')
        end_date = self.request.query_params.get('end_date', '')
        search = self.request.query_params.get('search', '')

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if action:
            queryset = queryset.filter(action=action)

        if model:
            queryset = queryset.filter(model__icontains=model)

        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)

        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)

        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(detail__icontains=search) |
                Q(model__icontains=search)
            )

        return queryset.order_by('-timestamp')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            try:
                page_num = int(request.GET.get('page', 0))
                limit_num = int(request.GET.get('limit', 50))
            except (ValueError, TypeError):
                return Response({"error": "Parámetros 'page' y 'limit' deben ser numéricos"}, status=status.HTTP_400_BAD_REQUEST)
            total = queryset.count()

            if limit_num == -1:
                paginated = queryset
            else:
                start = page_num * limit_num
                end = limit_num * (page_num + 1)
                paginated = queryset[start:end]

            serializer = RecordSerializer(paginated, many=True)

            return Response({
                'status': 'success',
                'records': serializer.data,
                'total': total,
                'page': page_num,
                'limit': limit_num
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


DOC_TYPE_TRANSLATIONS = {
    'reserva': 'Solicitud de Reserva',
    'entrega': 'Acta de Entrega',
    'horas_extra': 'Horas Extras',
    'payments': 'Canon de Pagos',
    'warranties': 'Registro de Garantías',
    'warranty_request': 'Solicitud Dev. Garantía',
    'warranty_return': 'Conformidad de Garantía',
    'warranty_damage': 'Ejecución de Garantía',
}


class AvailableByRentalApi(generics.GenericAPIView):
    """
    Retorna alquileres con los documentos que se pueden imprimir
    basándose en los datos reales de cada alquiler.
    """
    permission_classes = [IsAuthenticated, HasModulePermission]
    rbac_module = 'records'

    def get(self, request, *args, **kwargs):
        try:

            from leases.models import Rental, Selected_Product
            from leases.serializer import RentalsSerializer
            from financials.models import Payment, Warranty_Movement, Event_Damage

            rentals = Rental.objects.exclude(state_id=5).select_related(
                'state', 'customer'
            ).order_by('-id')

            rental_ids = [r.id for r in rentals]

            customer_ids = [r.customer_id for r in rentals if r.customer_id]
            from customers.models import Contact
            contact_map = {}
            for c in Contact.objects.filter(customer_id__in=customer_ids):
                contact_map.setdefault(c.customer_id, []).append(c)

            sp_map = {}
            for sp in Selected_Product.objects.filter(rental_id__in=rental_ids):
                sp_map.setdefault(sp.rental_id, []).append(sp)

            payment_map = {}
            for p in Payment.objects.filter(rental_id__in=rental_ids):
                payment_map.setdefault(p.rental_id, []).append(p)

            wm_map = {}
            for wm in Warranty_Movement.objects.filter(rental_id__in=rental_ids):
                wm_map.setdefault(wm.rental_id, []).append(wm)

            sp_ids = [sp.id for sps in sp_map.values() for sp in sps]

            aha_map = {}
            from leases.models import Additional_Hour_Applied
            for aha in Additional_Hour_Applied.objects.filter(selected_product_id__in=sp_ids):
                aha_map.setdefault(aha.selected_product_id, True)

            ed_sp_ids = set(Event_Damage.objects.filter(
                selected_product_id__in=sp_ids
            ).values_list('selected_product_id', flat=True))

            result = []
            for rental in rentals:
                available_docs = []

                customer = rental.customer
                contacts = contact_map.get(customer.id, []) if customer else []
                selected_products = sp_map.get(rental.id, [])
                payments = payment_map.get(rental.id, [])
                warranty_movements = wm_map.get(rental.id, [])

                has_customer_data = customer and len(contacts) > 0
                has_products = len(selected_products) > 0
                has_payments = len(payments) > 0
                has_warranties = len(warranty_movements) > 0
                has_balance = any(w.balance > 0 for w in warranty_movements) if has_warranties else False

                if has_customer_data:
                    available_docs.append({
                        'type': 'reserva',
                        'name': DOC_TYPE_TRANSLATIONS['reserva'],
                    })

                if has_products:
                    available_docs.append({
                        'type': 'entrega',
                        'name': DOC_TYPE_TRANSLATIONS['entrega'],
                        'product_ids': [sp.id for sp in selected_products],
                    })

                    for sp in selected_products:
                        if aha_map.get(sp.id, False):
                            available_docs.append({
                                'type': 'horas_extra',
                                'name': DOC_TYPE_TRANSLATIONS['horas_extra'],
                                'product_ids': [sp.id],
                            })
                            break

                if has_payments:
                    available_docs.append({
                        'type': 'payments',
                        'name': DOC_TYPE_TRANSLATIONS['payments'],
                    })

                if has_warranties:
                    available_docs.append({
                        'type': 'warranties',
                        'name': DOC_TYPE_TRANSLATIONS['warranties'],
                    })

                if has_balance:
                    available_docs.append({
                        'type': 'warranty_request',
                        'name': DOC_TYPE_TRANSLATIONS['warranty_request'],
                    })
                    available_docs.append({
                        'type': 'warranty_return',
                        'name': DOC_TYPE_TRANSLATIONS['warranty_return'],
                    })

                    for sp in selected_products:
                        if sp.id in ed_sp_ids:
                            available_docs.append({
                                'type': 'warranty_damage',
                                'name': DOC_TYPE_TRANSLATIONS['warranty_damage'],
                                'product_ids': [sp.id],
                            })
                            break

                if len(available_docs) > 0:
                    customer_name = ''
                    if customer:
                        if customer.institution_name:
                            customer_name = customer.institution_name
                        elif contacts:
                            customer_name = contacts[0].name

                    result.append({
                        'id': rental.id,
                        'contract_number': rental.contract_number or '',
                        'customer_name': customer_name,
                        'state_name': rental.state.name if rental.state else '',
                        'date': rental.created_at.strftime('%d/%m/%Y') if rental.created_at else '',
                        'available_documents': available_docs,
                    })

            return Response({
                'status': 'success',
                'rentals': result,
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
