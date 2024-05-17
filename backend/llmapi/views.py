from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import kimi_api
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

kimi_bot = kimi_api.KimiBot()

class SimpleAPIView(APIView):
    #@csrf_exempt
    def get(self, request, *args, **kwargs):
        # 返回一个字符串的响应
        message = kimi_bot.response()
        response = Response({"message":message}, status=status.HTTP_200_OK)
        #response['Access-Control-Allow-Origin'] = 'http://localhost:8089'
        return response

    #@api_view(['POST'])
    def post(self,request):
        print('接收到数据....')
        print('REQUEST:',request)
        form_data = request.data   # request.data 中包含了传送过来的 formData
        print(form_data)
        prompt = {}
        # 在这里处理你的表单数据
        prompt['context'] = form_data.get('context')
        prompt['goal'] = form_data.get('goal')
        prompt['style'] = form_data.get('style')
        prompt['tone ']= form_data.get('tone')
        prompt['audience'] = form_data.get('audience')
        prompt['output'] = form_data.get('output')
        
        message = kimi_bot.response(**prompt)
        response = Response({"message":message}, status=status.HTTP_200_OK) 
        return response
