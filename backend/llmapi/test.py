from django.http import JsonResponse
import time
from django.views.decorators.http import require_http_methods
import json


@require_http_methods(["POST"])
def process_request(request):
    try:
        # 解析 JSON 数据
        data = json.loads(request.body)
        delay = float(data.get('delay', 60))

        # 参数验证
        if not (0 <= delay <= 60):
            return JsonResponse(
                {"status": "error", "message": "Delay 0-60 seconds"},
                status=400
            )

        # 模拟处理延时
        time.sleep(delay)

        # 成功响应
        return JsonResponse({
            "status": "completed",
            "delay_seconds": delay,
            "result": f"Processed after {delay}s"
        })

    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON format"},
            status=400
        )

s = {
    "message": "{\n   \"campaignData\": {\n     \"stage\": \"考虑阶段(Consideration)或意向阶段(Intent)\",\n     \"objectives\": \"确立品牌的价值观和独特卖点，吸引受众的兴趣并引导他们考虑产品或服务的实用性和效益。\"\n   },\n   \"personaData\": {\n     \"desc\": \"目标受众可能是小创业主、小品牌主或一线营销人员，在有限的预算下，寻找有效的营销策略。\",\n     \"motives\": \"对高效精准的营销方法的追求；对品牌价值观的认同；希望在竞争激烈的市场中获得优势。\"\n   },\n   \"productData\": {\n     \"name\": \"此处为假设产品名，如 “步步为营营销策略”\",\n     \"usp\": \"基于营销漏斗的精准营销效果和步步为营的服务理念\",\n     \"brandValues\": \"效果至上\"\n   },\n   \"senarioData\": {\n     \"places\": \"适合在线环境下使用，如微信群、社交媒体、公司官网等，使用实时互动的方式分享营销知识。\",\n     \"emotionTags\": [\"激励(Inspirational)\", \"信任(Trust)\", \"共赢(Win-Win)\"]\n   },\n   \"advicesData\": [\n     {\n       \"issue\": \"文案中的'🔥 **让我们给你的事业** _步步为营_ **的策略与效果！_'未明确表达产品或服务的具体名称。\",\n       \"suggestion\": \"建议将 '步步为营的策略与效果' 更换为具体的服务或产品名称，以提高品牌识别度和清晰度。\"\n     },\n     {\n       \"issue\": \"品牌价值观虽然提到，但未具体展开。\",\n       \"suggestion\": \"详细阐述品牌价值观如《效果至上》具体如何体现在产品和服务上，以便受众理解其重要性。\"\n     },\n     {\n       \"issue\": \"产品独特卖点 '注重营销效果' 并未详细解析，',\n       \"suggestion\": \"建议使用具体案例或数据来展示独特卖点，增强说服力。\"\n     },\n     {\n       \"issue\": \"微信群被提及为交流渠道，但没有明确其在整个营销策略中的作用。\",\n       \"suggestion\": \"应该进一步阐述微信群将如何帮助受众实现《步步为营》的品牌承诺，以及如何在群内开展营销活动。\"\n     },\n     {\n       \"issue\": \"文案末尾突然断开，没有给出完整的行动呼吁。\",\n       \"suggestion\": \"在文案末尾添加明确的行动呼吁，如 '立即加入我们的微信群，开启你的营销成功之旅！'\"\n     }\n   ]\n}"
}

