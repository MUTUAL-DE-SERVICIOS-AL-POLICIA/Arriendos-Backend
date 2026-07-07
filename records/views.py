"""
Vistas para la app de registros (auditoria interna).

Endpoints:
- GET /api/records/ - Lista paginada de registros de auditoria

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
            page_num = int(request.GET.get('page', 0))
            limit_num = int(request.GET.get('limit', 50))
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
