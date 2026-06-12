"""WorkSphere HR - Attendance API URLs"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ClockInView, ClockOutView, AttendanceViewSet

router = DefaultRouter()
router.register('', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('clock-in/', ClockInView.as_view(), name='clock_in'),
    path('clock-out/', ClockOutView.as_view(), name='clock_out'),
] + router.urls
