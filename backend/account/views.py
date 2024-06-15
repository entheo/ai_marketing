from django.middleware.csrf import get_token
from django.shortcuts import render
from datetime import timedelta,datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from marketing.models import Brand
from .models import Users 
from rest_framework.permissions import IsAuthenticated

def get_created_brands(username):
    try:
        creator = Users.objects.get(username=username)
        #res = creator.brands.all()
        res = creator.brands.values_list('chinese_name',flat=True)
    except ObjectDoesNotExist:
        print(f"用户{username}不存在")
        raise ValueError(f"{username} 用户不存在")
    return res

def get_created_campaigns(username):
   try:
       creator = Users.objects.get(username=username)
       res = creator.campaigns.values_list('title',flat=True)
   except ObjectDoesNotExist:
       print(f"用户{username}不存在")
       raise ValueError (f"{username}用户不存在")
   return res


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
    
    def get_tokens_for_user(self,user,keep_logged_in_for_days):
       refresh = RefreshToken.for_user(user)
       refresh.lifetime = timedelta(days=keep_logged_in_for_days)
       access_token = refresh.access_token
       print('access_token',access_token)

       return {
            'refresh': str(refresh),
            'access': str(access_token),
        }

    def post(self, request):
        keep_logged_in_for_days = int(request.data.get('keep_logged_in_for_days', 7))
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        print('USER:',user)
        if user:
            token = self.get_tokens_for_user(user,keep_logged_in_for_days)
            login(request,user)
            csrf_token = get_token(request)
            #created_brands = get_created_brands(username)
            resp = Response({"message": "loggedIn",'username':username,'token':token,'csrf_token':csrf_token}, status=status.HTTP_200_OK)
            resp.set_cookie('csrf_token',csrf_token)
            return resp    
        return Response({"message": "用户名或密码错误"}, status=status.HTTP_400_BAD_REQUEST)

class AuthAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 使用JWT验证
    
    def get(self, request, *args, **kwargs):
        print('开始验证')
        try:
          created_brands = get_created_brands(request.user.username)
          created_campaigns = get_created_campaigns(request.user.username)
        except:
            pass
        return Response({'auth':'success','username':request.user.username,'created_brands':created_brands,'created_campaigns':created_campaigns})
