from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer

class RegisterAPIView(APIView):
    def post(self, request):
        print('Request:',request.data)
        serializer = UserRegistrationSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request):
        keep_logged_in_for_days = int(request.data.get('keep_logged_in_for_days', 7))
        print(type(keep_logged_in_for_days),keep_logged_in_for_days)
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        print('USER:',user)
        if user:
            login(request,user)
            if keep_logged_in_for_days > 0:  # 验证用户选择的天数是否大于0
            # 设置session过期时间为指定天数
                seconds_to_keep_logged_in = keep_logged_in_for_days * 86400  # 24 hours * 60 minutes * 60 seconds
                request.session.set_expiry(seconds_to_keep_logged_in) 
            # 这里简化处理，实际项目中应当返回token
            return Response({"message": "loggedIn",'username':username}, status=status.HTTP_200_OK)
        return Response({"message": "用户名或密码错误"}, status=status.HTTP_400_BAD_REQUEST)

