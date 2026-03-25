from django.urls import path
from .views import save_report,get_report

urlpatterns = [
    path('save-report/', save_report),
    path('report/<int:report_id>/', get_report),
]
