from django.urls import path
from .views import RegisterAPIView, LoginAPIView, AuthAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/',LoginAPIView.as_view(),name='login'),
    path('auth/',AuthAPIView.as_view(),name='auth'),
]
