from django.urls import path
from .views import SimpleAPIView

urlpatterns = [
    path('response/', SimpleAPIView.as_view(), name='llmresponse'),
]
