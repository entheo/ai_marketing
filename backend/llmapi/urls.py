from django.urls import path
from .views import SimpleAPIView, format_prompt, get_advice,test_response

urlpatterns = [
    path('response/', SimpleAPIView.as_view(), name='llmresponse'),
    path('assistant/',format_prompt, name='format'),
    path('advice/',get_advice, name='advice'),
    path('test/',test_response,name='test')
]
