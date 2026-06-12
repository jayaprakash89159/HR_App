"""WorkSphere HR - Attendance Web URLs"""
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
app_name = 'attendance'
urlpatterns = [
    path('', login_required(lambda r: render(r, 'attendance/modern_attendance.html')), name='my_attendance'),
    path('my/', login_required(lambda r: render(r, 'attendance/modern_attendance.html')), name='my_attendance_list'),
    path('clock/', login_required(lambda r: render(r, 'attendance/clock.html')), name='clock'),
    path('od/', login_required(lambda r: render(r, 'attendance/od.html')), name='od'),
    path('short-time-off/', login_required(lambda r: render(r, 'attendance/sto.html')), name='short_time_off'),
    path('team/', login_required(lambda r: render(r, 'attendance/team.html')), name='team'),
]
