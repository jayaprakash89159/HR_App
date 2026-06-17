"""WorkSphere HR - Leave Web URLs"""
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.authentication.utils import employee_portal_only, manager_or_hr_portal_only

app_name = 'leave'

urlpatterns = [
    path('',             employee_portal_only(lambda r: render(r, 'leave/modern_leave.html')), name='my_leaves'),
    path('apply/',       employee_portal_only(lambda r: render(r, 'leave/modern_leave.html')), name='apply'),
    path('my-leaves/',   employee_portal_only(lambda r: render(r, 'leave/modern_leave.html')), name='my_leaves_list'),
    path('balance/',     employee_portal_only(lambda r: render(r, 'leave/modern_leave.html')), name='balance'),
    path('holidays/',    login_required(lambda r: render(r, 'leave/holidays.html')),           name='holidays'),
    path('requests/',    manager_or_hr_portal_only(lambda r: render(r, 'leave/leave_requests.html')), name='requests'),
    path('approvals/',   manager_or_hr_portal_only(lambda r: render(r, 'leave/leave_requests.html')), name='approvals'),
]
