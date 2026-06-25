from django.contrib.auth.models import User
from .models import Room
from rooms.serializers import RoomSerializer
from .models import Assign
from rest_framework import serializers

class UserCustomSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'role')

    def get_role(self, obj):
        try:
            from roles.models import UserRole
            user_role = UserRole.objects.get(user=obj)
            return {
                'id': user_role.role.id,
                'name': user_role.role.name,
            }
        except:
            return None


class AssignSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Assign
        fields = '__all__'
class AssignsSerializer(serializers.ModelSerializer):
    user = UserCustomSerializer()
    room = RoomSerializer()
    class Meta:
        model = Assign
        fields = '__all__'