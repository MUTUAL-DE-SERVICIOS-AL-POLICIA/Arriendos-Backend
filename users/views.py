from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserCustomSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework import status

# Create your views here.
class User_Ldap(APIView):
    def get(self, request):
        #users = serializers.serialize("json", User.objects.all().exclude('password'))
        #sers = User.objects.all()
        users = User.objects.all()
        serializer = UserCustomSerializer(users, many=True)
        return Response(serializer.data)
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'El usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'El correo ya existe'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        user.save()
        return Response({"message":"Usuario registrado con exito", "user": user.id, "username": user.username, "email": user.email, "first_name": user.first_name, "last_name": user.last_name}, status=status.HTTP_201_CREATED)
