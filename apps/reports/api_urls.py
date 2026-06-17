"""WorkSphere HR - Reports API URLs"""
from django.urls import path
from .views import ReportsSummaryAPIView, AttendanceReportAPIView

urlpatterns = [
    path('summary/', ReportsSummaryAPIView.as_view(), name='reports_summary'),
    path('attendance/', AttendanceReportAPIView.as_view(), name='reports_attendance'),
]
