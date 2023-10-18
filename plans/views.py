from rest_framework.response import Response
from rest_framework import generics
from .models import Plan
from .serializer import PlanSerializer


class Plan_Api(generics.ListCreateAPIView):
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()