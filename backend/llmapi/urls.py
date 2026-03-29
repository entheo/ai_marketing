from django.urls import path
from .views import (
    SimpleAPIView,
    format_prompt,
    get_advice,
    get_advice_stream,
    apply_stage_feedback,
    try_stage_transition,
    test_response,
)

urlpatterns = [
    path('response/', SimpleAPIView.as_view(), name='llmresponse'),
    path('assistant/', format_prompt, name='format'),

    # 主问答
    path('advice/', get_advice, name='advice'),

    # 流式问答
    path('advice/stream/', get_advice_stream, name='advice_stream'),

    # 右侧轻确认反馈
    path('stage-feedback/', apply_stage_feedback, name='stage_feedback'),

    # 阶段切换
    path('stage-transition/', try_stage_transition, name='stage_transition'),

    path('test/', test_response, name='test'),
]
