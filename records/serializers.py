"""
Serializers para la app de registros (auditoria).

Serializa los registros de auditoria (users.Record) para
su consulta a traves de la API REST.

Autor: Dilan Torrez
Fecha: 2026
"""

from rest_framework import serializers
from users.models import Record

ACTION_TRANSLATIONS = {
    'create': 'Creación',
    'update': 'Actualización',
    'delete': 'Eliminación',
}

MODEL_TRANSLATIONS = {
    'Additional_Hour_Applied': 'Hora Adicional Aplicada',
    'Contact': 'Contacto',
    'Customer': 'Cliente',
    'Customer_type': 'Tipo de Cliente',
    'Event_Type': 'Tipo de Evento',
    'HourRange': 'Rango de Horas',
    'Payment': 'Pago',
    'Plan': 'Plan',
    'Price': 'Precio',
    'Price_Additional_Hour': 'Precio Hora Adicional',
    'Product': 'Producto',
    'Property': 'Inmueble',
    'Rate': 'Tarifa',
    'RateRequirement': 'Requisito de Tarifa',
    'Rental': 'Arriendo',
    'Requirement': 'Requisito',
    'Requirement_Delivered': 'Requisito Entregado',
    'Role': 'Rol',
    'RolePermission': 'Permiso de Rol',
    'Room': 'Salón',
    'Selected_Product': 'Producto Seleccionado',
    'State': 'Estado',
    'Sub_Room': 'Sub-ambiente',
    'User': 'Usuario',
    'UserRole': 'Rol de Usuario',
    'Warranty_Movement': 'Movimiento de Garantía',
}


class RecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', default='sistema', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    action_display = serializers.SerializerMethodField()
    model_display = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Record
        fields = ['id', 'user', 'username', 'user_full_name', 'action', 'action_display', 'model', 'model_display', 'detail', 'description', 'instance_id', 'timestamp']

    def _get_user_name(self, user):
        if user:
            first = user.first_name or ''
            last = user.last_name or ''
            full = f"{first} {last}".strip()
            return full if full else user.username
        return 'Sistema'

    def get_user_full_name(self, obj):
        return self._get_user_name(obj.user)

    def get_action_display(self, obj):
        return ACTION_TRANSLATIONS.get(obj.action, obj.action)

    def get_model_display(self, obj):
        return MODEL_TRANSLATIONS.get(obj.model, obj.model)

    def get_description(self, obj):
        detail = obj.detail or ''
        user_name = self._get_user_name(obj.user)

        if detail.startswith('El usuario:'):
            parts = detail.split(' ', 3)
            if len(parts) >= 4:
                return f"El usuario: {user_name} {parts[3]}"
            return detail

        if user_name and user_name != 'Sistema':
            return f"{user_name} → {detail}"

        return detail
