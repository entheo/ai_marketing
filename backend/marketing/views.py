from django.shortcuts import render
from rest_framework.views import APIView
from account.utils import get_current_user
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# Create your views here.

from rest_framework import viewsets
from .models import Brand
from .serializers import BrandSerializer

class BrandAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 使用JWT验证

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = BrandSerializer(data=request.data)
        print(serializer)
        print(serializer.is_valid())
        print(serializer.errors) 
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class BrandViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    '''
    def create(self, request, *args, **kwargs):
        print('请求体:', request.data)  # 打印请求数据
        return super().create(request, *args, **kwargs)
    '''

