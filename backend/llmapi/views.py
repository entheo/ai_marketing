from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import kimi_api
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
import json, re
from django.http import JsonResponse


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
        form_data = request.data   # request.data 中包含了传送过来的 formData
        print(form_data)
        message = kimi_bot.response(**form_data)
        response = Response({"message":message}, status=status.HTTP_200_OK) 
        return response

@csrf_exempt
def format_prompt(request):
    if request.method == 'POST':
        print('REQUEST：',request.body);
        data = json.loads(request.body.decode('utf-8'))  # 解析JSON数据
        print('接收到的信息：',data)
        
        #messages = data['_value']
        res = kimi_bot.response(**data)
    return JsonResponse(res,safe=False)


#获取分析与建议
@csrf_exempt
def get_advice(request):
    if request.method == 'POST':
        print('REQUEST：',request.body);
        data = json.loads(request.body.decode('utf-8'))
        print('RECEIVED DATA:',data)
        response = kimi_bot.response(**data)
        print('建议的数据类型:',type(response))
        print('已获得建议:',response)
        #避免建议中包含markdown语法导致json解析失败
        if response.startswith("```json") and response.endswith("```"):
            print("注意：服务器返回Markdown语法，须做对应清理")
            json_string = response[7:-3].strip()
        else:
            json_string = response
        try:
            res = json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"json解析错误:{e}")
    return JsonResponse(res, safe=False)

def format_data(raw_data):
    print('Raw_Data:',raw_data)
    task_sections = re.findall(r'\*\*(.*?)\*\*\s*\(\[\#(.*?)\#\]\)\s*\n(.+?)(?=\n\n\*\*|\n\n###|\Z)', raw_data, re.DOTALL)
    
    formatted_data = {}
    for section in task_sections:
        title, key, content = section
        content_clean = re.sub(r'\n+', ' ', content.strip())  # 日程重复换行替换为一个空格。
        formatted_data[key] = {'title': title, 'content': content_clean}

    advices = re.findall(r'\*\*(\d+\..*?)\*\*\n   - (.+?)(?=\n\n\*\*|\n\n###|\Z)', raw_data, re.DOTALL)
    print("Advices:",advices)
    advices_list = [{'index': advice[0], 'content': advice[1].strip()} for advice in advices]
    print("advices_list:",advices_list)
    formatted_data['advices'] = advices_list
    print('formatted_data:',formatted_data) 
    '''
    if 'emotions' in formatted_data:
        emotions_content = formatted_data['emotions']['content']
        emotions_list = re.split(r'，|,|\s+和\s+', emotions_content)
        formatted_data['emotions']['content'] = [emotion.strip() for emotion in emotions_list if emotion]
    '''
    return JsonResponse(formatted_data)



def extract_information(raw_data):
    # 匹配每一个段落标题和内容
    pattern = r'#### (.*?)\(\[\#(.*?)\#\]\)\n(.*?)\n\n'
    matches = re.findall(pattern, raw_data, re.DOTALL)

    # 初始信息字典
    information = {}

    # 将匹配项以键值对的形式存入信息字典
    for match in matches:
        key = match[1]
        # 对于 'product_usp' 和 'brand_value' 分条列出
        if key in ['product_usp', 'brand_value']:
            value = [v.strip() for v in match[2].split('\n') if v.strip()]
        else:
            value = match[2].strip().replace('\n', ' ')
        information[key] = value

    # 获取 advices 部分
    advices_pattern = r'\n(\d+\.\s*\*\*(.*?)\*\*)\n\s*-\s*\*\*(.*?)\*\*:(.*?)\n'
    advice_matches = re.findall(advices_pattern, raw_data, re.DOTALL)
    advices = [{'index': m[0].strip(),
                'title': m[1].strip(),
                'issue': m[2].strip(),
                'suggestion': m[3].strip().replace('\n', ' ')}
               for m in advice_matches]

    information['advices'] = advices

    # 对于 'emotions' 需要分隔为数组
    if 'emotions' in information:
        emotions_content = information['emotions']
        information['emotions'] = [e.strip() for e in re.split(r'、|,', emotions_content) if e.strip()]

    return information



@csrf_exempt
def test_response(request):
    if request.method=='POST':
        print('REQUEST：',request.body);
        data = json.loads(request.body.decode('utf-8'))  # 解析JSON数据
        print('接收到的信息：',data)
        
        res = json.dumps(data)
    return JsonResponse(res,safe=False)
