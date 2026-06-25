from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Module, Permission, Role, RolePermission, UserRole
from .serializers import (
    ModuleSerializer, PermissionSerializer,
    RoleSerializer, RoleCreateSerializer,
    UserRoleSerializer, UserRoleCreateSerializer,
    UserWithRoleSerializer
)
from users.permissions import HasViewUserPermission
import math


class Module_List_View(generics.ListAPIView):
    queryset = Module.objects.filter(is_active=True)
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        modules = self.get_queryset()
        serializer = self.serializer_class(modules, many=True)
        return Response({
            "status": "success",
            "modules": serializer.data
        })


class Permission_List_View(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        permissions = self.get_queryset()
        serializer = self.serializer_class(permissions, many=True)
        return Response({
            "status": "success",
            "permissions": serializer.data
        })


class Role_List_Create_View(generics.GenericAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', self.queryset.count()))
        search_param = request.GET.get('search', '')
        start_num = page_num * limit_num
        end_num = limit_num * (page_num + 1)

        roles = Role.objects.all()
        if search_param:
            roles = roles.filter(name__icontains=search_param)

        total = roles.count()
        serializer = RoleSerializer(roles[start_num:end_num], many=True)

        return Response({
            "status": "success",
            "total": total,
            "page": page_num,
            "last_page": math.ceil(total / limit_num) if limit_num > 0 else 0,
            "roles": serializer.data
        })

    def post(self, request, *args, **kwargs):
        serializer = RoleCreateSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            return Response({
                "status": "success",
                "data": RoleSerializer(role).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "fail",
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class Role_Detail_View(generics.GenericAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            role = Role.objects.get(pk=pk)
            serializer = RoleSerializer(role)
            return Response({
                "status": "success",
                "data": serializer.data
            })
        except Role.DoesNotExist:
            return Response({
                "status": "fail",
                "message": "Rol no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk, *args, **kwargs):
        try:
            role = Role.objects.get(pk=pk)
            serializer = RoleCreateSerializer(role, data=request.data, partial=True)
            if serializer.is_valid():
                role = serializer.save()
                return Response({
                    "status": "success",
                    "data": RoleSerializer(role).data
                })
            return Response({
                "status": "fail",
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Role.DoesNotExist:
            return Response({
                "status": "fail",
                "message": "Rol no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, *args, **kwargs):
        try:
            role = Role.objects.get(pk=pk)
            if UserRole.objects.filter(role=role).exists():
                return Response({
                    "status": "fail",
                    "message": "No se puede eliminar un rol asignado a usuarios"
                }, status=status.HTTP_400_BAD_REQUEST)
            role.delete()
            return Response({
                "status": "success",
                "message": "Rol eliminado correctamente"
            })
        except Role.DoesNotExist:
            return Response({
                "status": "fail",
                "message": "Rol no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)


class UserRole_Assign_View(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UserRoleCreateSerializer(data=request.data)
        if serializer.is_valid():
            user_role = serializer.save()
            return Response({
                "status": "success",
                "data": UserRoleSerializer(user_role).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "fail",
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserRole_List_View(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_roles = UserRole.objects.select_related('user', 'role').all()
        serializer = UserRoleSerializer(user_roles, many=True)
        return Response({
            "status": "success",
            "user_roles": serializer.data
        })


class UserRole_Detail_View(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            user_role = UserRole.objects.get(pk=pk)
            user_role.delete()
            return Response({
                "status": "success",
                "message": "Rol removido del usuario"
            })
        except UserRole.DoesNotExist:
            return Response({
                "status": "fail",
                "message": "Asignacion no encontrada"
            }, status=status.HTTP_404_NOT_FOUND)


class MyPermissions_View(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            user_role = UserRole.objects.get(user=user)
            role = user_role.role
            role_permissions = RolePermission.objects.filter(role=role).select_related('module')
            permissions = []
            for rp in role_permissions:
                for perm in rp.permissions.all():
                    permissions.append(f"{rp.module.codename}.{perm.codename}")
            return Response({
                "status": "success",
                "role": role.name,
                "permissions": permissions
            })
        except UserRole.DoesNotExist:
            return Response({
                "status": "success",
                "role": None,
                "permissions": []
            })
