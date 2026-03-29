from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import kimi_api
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, StreamingHttpResponse
import json
from . import test
from .self_value_bot import SelfValueBot

FRONTEND_ORIGIN = "http://localhost:8082"

kimi_bot = kimi_api.KimiBot()
self_value_bot = SelfValueBot(client=kimi_bot.client, model=kimi_bot.model)


def _build_cors_response(payload=None, status_code=200):
    response = JsonResponse(payload or {}, status=status_code, safe=isinstance(payload, dict) is False)
    response["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def _handle_options_request():
    response = JsonResponse({}, status=200)
    response["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def _parse_request_json(request):
    try:
        body_text = request.body.decode("utf-8").strip()
        if not body_text:
            return None, JsonResponse({"error": "Empty request body."}, status=400)
        data = json.loads(body_text)
        return data, None
    except json.JSONDecodeError as e:
        return None, JsonResponse({"error": f"Invalid JSON: {e}"}, status=400)


class SimpleAPIView(APIView):
    def get(self, request, *args, **kwargs):
        message = kimi_bot.response()
        response = Response({"message": message}, status=status.HTTP_200_OK)
        return response

    def post(self, request):
        form_data = request.data
        message = kimi_bot.response(**form_data)
        response = Response({"message": message}, status=status.HTTP_200_OK)
        return response


@csrf_exempt
def format_prompt(request):
    if request.method == "POST":
        data, error_response = _parse_request_json(request)
        if error_response:
            return error_response

        res = kimi_bot.response(**data)
        return JsonResponse(res, safe=False)

    return JsonResponse({"error": "Only POST method is allowed."}, status=405)


@csrf_exempt
def get_advice(request):
    """
    主问答接口
    - 非 self_value: 走原 kimi_bot.response
    - self_value: 直接返回前端可消费结构
      {
        "message": {...},
        "stage": {...},
        "meta": {...}
      }
    """
    if request.method == "OPTIONS":
        return _handle_options_request()

    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    data, error_response = _parse_request_json(request)
    if error_response:
        return error_response

    try:
        if data.get("type") == "self_value":
            result = self_value_bot.self_value_frontend_response(**data)

            if not isinstance(result, dict):
                return JsonResponse(
                    {"error": "SelfValueBot must return a dict response."},
                    status=500
                )
        else:
            result = kimi_bot.response(**data)

        return _build_cors_response(result, status_code=200)

    except Exception as e:
        response = JsonResponse({"error": f"Backend error: {str(e)}"}, status=500)
        response["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
        return response


@csrf_exempt
def apply_stage_feedback(request):
    """
    右侧轻确认反馈接口

    期望入参：
    {
      "type": "self_value",
      "conversation_id": "conv_xxx",
      "stage_state": {...},
      "candidate_id": "c_xxx",
      "action": "confirmed" | "rejected" | "revised",
      "user_note": "可选"
    }

    返回：
    {
      "stage": {...},
      "meta": {...}
    }
    """
    if request.method == "OPTIONS":
        return _handle_options_request()

    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    data, error_response = _parse_request_json(request)
    if error_response:
        return error_response

    if data.get("type") != "self_value":
        return JsonResponse(
            {"error": "apply_stage_feedback only supports self_value."},
            status=400
        )

    candidate_id = data.get("candidate_id", "")
    action = data.get("action", "")
    user_note = data.get("user_note", "")

    if not candidate_id:
        return JsonResponse({"error": "candidate_id is required."}, status=400)

    if action not in ("confirmed", "rejected", "revised"):
        return JsonResponse(
            {"error": "action must be one of: confirmed, rejected, revised."},
            status=400
        )

    try:
        result = self_value_bot.apply_stage_feedback_frontend(
            candidate_id=candidate_id,
            action=action,
            user_note=user_note,
            **data,
        )
        return _build_cors_response(result, status_code=200)

    except Exception as e:
        response = JsonResponse({"error": f"Backend error: {str(e)}"}, status=500)
        response["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
        return response


@csrf_exempt
def try_stage_transition(request):
    """
    阶段切换接口

    期望入参：
    {
      "type": "self_value",
      "conversation_id": "conv_xxx",
      "stage_state": {...}
    }

    返回：
    {
      "stage": {...},
      "meta": {...}
    }
    """
    if request.method == "OPTIONS":
        return _handle_options_request()

    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    data, error_response = _parse_request_json(request)
    if error_response:
        return error_response

    if data.get("type") != "self_value":
        return JsonResponse(
            {"error": "try_stage_transition only supports self_value."},
            status=400
        )

    try:
        result = self_value_bot.try_stage_transition_frontend(**data)
        return _build_cors_response(result, status_code=200)

    except Exception as e:
        response = JsonResponse({"error": f"Backend error: {str(e)}"}, status=500)
        response["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
        return response


@csrf_exempt
def get_advice_stream(request):
    """
    流式问答接口

    仅支持 self_value。
    事件协议：
    - message_chunk
    - message_done
    - stage_done
    - error
    """
    if request.method == "OPTIONS":
        return _handle_options_request()

    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    data, error_response = _parse_request_json(request)
    if error_response:
        return error_response

    if data.get("type") != "self_value":
        return JsonResponse(
            {"error": "Streaming only supports self_value for now."},
            status=400
        )

    def event_stream():
        try:
            for item in self_value_bot.self_value_stream(**data):
                yield json.dumps(item, ensure_ascii=False) + "\n"
        except Exception as e:
            yield json.dumps({
                "event": "error",
                "message": f"Streaming backend error: {str(e)}"
            }, ensure_ascii=False) + "\n"

    response = StreamingHttpResponse(
        event_stream(),
        content_type="application/x-ndjson; charset=utf-8"
    )
    response["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


def format_data(raw_data):
    print('Raw_Data:', raw_data)
    import re

    task_sections = re.findall(
        r'\*\*(.*?)\*\*\s*\(\[\#(.*?)\#\]\)\s*\n(.+?)(?=\n\n\*\*|\n\n###|\Z)',
        raw_data,
        re.DOTALL
    )

    formatted_data = {}
    for section in task_sections:
        title, key, content = section
        content_clean = re.sub(r'\n+', ' ', content.strip())
        formatted_data[key] = {'title': title, 'content': content_clean}

    advices = re.findall(
        r'\*\*(\d+\..*?)\*\*\n   - (.+?)(?=\n\n\*\*|\n\n###|\Z)',
        raw_data,
        re.DOTALL
    )
    advices_list = [{'index': advice[0], 'content': advice[1].strip()} for advice in advices]
    formatted_data['advices'] = advices_list

    return JsonResponse(formatted_data)


def extract_information(raw_data):
    import re

    pattern = r'#### (.*?)\(\[\#(.*?)\#\]\)\n(.*?)\n\n'
    matches = re.findall(pattern, raw_data, re.DOTALL)

    information = {}

    for match in matches:
        key = match[1]
        if key in ['product_usp', 'brand_value']:
            value = [v.strip() for v in match[2].split('\n') if v.strip()]
        else:
            value = match[2].strip().replace('\n', ' ')
        information[key] = value

    advices_pattern = r'\n(\d+\.\s*\*\*(.*?)\*\*)\n\s*-\s*\*\*(.*?)\*\*:(.*?)\n'
    advice_matches = re.findall(advices_pattern, raw_data, re.DOTALL)
    advices = [
        {
            'index': m[0].strip(),
            'title': m[1].strip(),
            'issue': m[2].strip(),
            'suggestion': m[3].strip().replace('\n', ' ')
        }
        for m in advice_matches
    ]

    information['advices'] = advices

    if 'emotions' in information:
        emotions_content = information['emotions']
        information['emotions'] = [
            e.strip() for e in re.split(r'、|,', emotions_content) if e.strip()
        ]

    return information


@csrf_exempt
def test_response(request):
    test.process_request(request)
