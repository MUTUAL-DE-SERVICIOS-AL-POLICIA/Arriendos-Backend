from rest_framework.response import Response
from rest_framework import generics
from .models import Plan
from .serializer import PlanSerializer
from threadlocals.threadlocals import set_thread_variable
from rest_framework.permissions import IsAuthenticated


class Plan_Api(generics.ListCreateAPIView):
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        set_thread_variable('thread_user', request.user)
        return super().create(request, *args, **kwargs)