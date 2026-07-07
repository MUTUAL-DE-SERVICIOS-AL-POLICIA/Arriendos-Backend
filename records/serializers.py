"""
Serializers para la app de registros (auditoria).

Serializa los registros de auditoria (users.Record) para
su consulta a traves de la API REST.

Autor: Dilan Torrez
Fecha: 2026
"""

from rest_framework import serializers
from users.models import Record


class RecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', default='sistema', read_only=True)
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Record
        fields = ['id', 'user', 'username', 'user_full_name', 'action', 'model', 'detail', 'instance_id', 'timestamp']

    def get_user_full_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return 'Sistema'
