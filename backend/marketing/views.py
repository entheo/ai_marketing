from django.shortcuts import render
from rest_framework.views import APIView
from account.utils import get_current_user
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# Create your views here.

from rest_framework import viewsets
from .models import Brand,Campaign
from .serializers import BrandSerializer, CampaignSerializer

#Brand视图
class BrandAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 使用JWT验证

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

#Campaign视图
class CampaignAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,*args,**kwargs):
        print(request.data)
        serializer = CampaignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator = request.user)
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=400)
    
    def get(self,request,*args,**kwargs):
        permission_classes = [IsAuthenticated]
        res = Campaign.objects.filter(creator=request.user)
        serializer = CampaignSerializer(res,many=True)
        return Response(serializer.data,stauts=200)


