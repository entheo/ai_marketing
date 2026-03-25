from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import SelfValueReport


@csrf_exempt
def save_report(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    try:
        body_text = request.body.decode('utf-8').strip()
        if not body_text:
            return JsonResponse({"error": "Empty request body."}, status=400)

        data = json.loads(body_text)
    except json.JSONDecodeError as e:
        return JsonResponse({"error": f"Invalid JSON: {e}"}, status=400)

    report_text = data.get('report', '').strip()
    qa_history = data.get('qa_history',[])

    if not report_text:
        return JsonResponse({"error": "report is required."}, status=400)

    report = SelfValueReport.objects.create(
        user=request.user if request.user.is_authenticated else None,
        report_text=report_text,
        qa_history = qa_history
    )

    return JsonResponse({
        "id": report.id,
        "report_text": report.report_text,
        "created_at": report.created_at.isoformat()
    })

def get_report(request, report_id):
    if request.method != 'GET':
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)

    try:
        report = SelfValueReport.objects.get(id=report_id)
    except SelfValueReport.DoesNotExist:
        return JsonResponse({"error": "Report not found."}, status=404)

    return JsonResponse({
        "id": report.id,
        "report_text": report.report_text,
        "qa_history":report.qa_history,
        "created_at": report.created_at.isoformat()
    })
