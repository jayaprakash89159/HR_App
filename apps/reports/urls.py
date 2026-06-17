"""WorkSphere HR - Reports Web URLs"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard / Analytics
    path('', views.reports_dashboard, name='index'),
    path('analytics/', views.reports_dashboard, name='analytics'),

    # Report pages
    path('attendance/', views.attendance_report, name='attendance'),
    path('leave/', views.leave_report, name='leave'),
    path('employees/', views.employee_report, name='employees'),
    path('payroll/', views.payroll_report, name='payroll'),

    # Attendance exports
    path('attendance/export/csv/',   views.attendance_report_export_csv,   name='attendance_export_csv'),
    path('attendance/export/xlsx/',  views.attendance_report_export_excel,  name='attendance_export_excel'),
    path('attendance/export/pdf/',   views.attendance_report_export_pdf,    name='attendance_export_pdf'),

    # Leave exports
    path('leave/export/csv/',   views.leave_report_export_csv,   name='leave_export_csv'),
    path('leave/export/xlsx/',  views.leave_report_export_excel,  name='leave_export_excel'),

    # Employee exports
    path('employees/export/csv/',   views.employee_report_export_csv,   name='employee_export_csv'),
    path('employees/export/xlsx/',  views.employee_report_export_excel,  name='employee_export_excel'),
]
