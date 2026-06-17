"""WorkSphere HR - Attendance Web URLs"""
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.authentication.utils import employee_portal_only, manager_or_hr_portal_only


def attendance_context_view(request):
    """My Attendance page with server-side context for month/year selectors"""
    now = timezone.now()
    current_year = now.year
    months = [
        {'val': i, 'label': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i-1],
         'selected': i == now.month}
        for i in range(1, 13)
    ]
    years = list(range(current_year - 2, current_year + 1))
    return render(request, 'attendance/modern_attendance.html', {
        'months': months,
        'years': years,
        'current_year': current_year,
    })


app_name = 'attendance'
urlpatterns = [
    path('', employee_portal_only(attendance_context_view), name='my_attendance'),
    path('my/', employee_portal_only(attendance_context_view), name='my_attendance_list'),
    path('clock/', employee_portal_only(login_required(lambda r: render(r, 'attendance/clock.html'))), name='clock'),
    path('od/', employee_portal_only(login_required(lambda r: render(r, 'attendance/od.html'))), name='od'),
    path('short-time-off/', employee_portal_only(login_required(lambda r: render(r, 'attendance/sto.html'))), name='short_time_off'),
    path('team/', manager_or_hr_portal_only(login_required(lambda r: render(r, 'attendance/team.html'))), name='team'),
    path('team/approvals/', manager_or_hr_portal_only(login_required(lambda r: render(r, 'attendance/team_approvals.html'))), name='team_approvals'),
]
