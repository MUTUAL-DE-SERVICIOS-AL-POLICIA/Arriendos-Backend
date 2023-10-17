from rest_framework.response import Response
from rest_framework import status, generics
from .models import Plan
from .serializer import PlanSerializer
import math


class Plan_Api(generics.GenericAPIView):
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    
    def get(self, request, *args, **kwargs):
        page_num = int(request.GET.get('page', 0))
        limit_num = int(request.GET.get('limit', 10))
        start_num = (page_num) * limit_num
        end_num = limit_num * (page_num + 1)
        search_param = request.GET.get('search')
        plans = Plan.objects.all()
        total_plans = plans.count()
        if search_param:
            plans = plans.filter(title__icontains=search_param)
        serializer = self.serializer_class(plans[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_plans,
            "page": page_num,
            "last_page": math.ceil(total_plans/ limit_num),
            'plans': serializer.data
        })
    
    def post(self, request, *args, **kw):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"plan": serializer.data}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class Plan_Detail(generics.GenericAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    def get_plan(self, pk, *args, **kwargs):
        try:
            return Plan.objects.get(pk=pk)
        except:
            return None
        
    def get(self, request, pk, *args, **kw):
        plan = self.get_plan(pk=pk)
        if plan == None:
            return Response({"status": "fail", "message": f"Plan with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(plan)
        return Response({"status": "success", "data": {"plan": serializer.data}}, status=status.HTTP_200_OK)
    
    def patch(self, request, pk, *args, **kw):
        plan = self.get_plan(pk)
        if plan == None:
            return Response({"status": "fail", "message": f"Plan with id: {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": {"plan": serializer.data}}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)