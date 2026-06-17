"""WorkSphere HR — HR Admin URL patterns"""
from django.urls import path
from . import hr_views

urlpatterns = [
    path('departments/',       hr_views.hr_departments,       name='hr_departments'),
    path('designations/',      hr_views.hr_designations,      name='hr_designations'),
    path('locations/',         hr_views.hr_locations,         name='hr_locations'),
    path('users/',             hr_views.hr_users,             name='hr_users'),
    path('attendance/all/',    hr_views.hr_all_attendance,    name='hr_all_attendance'),
    path('leave/all/',         hr_views.hr_all_leaves,        name='hr_all_leaves'),
    path('regularization/',    hr_views.hr_regularization,    name='hr_regularization'),
    path('leave-types/',       hr_views.hr_leave_types,       name='hr_leave_types'),
    path('salary-structures/', hr_views.hr_salary_structures, name='hr_salary_structures'),
    path('payslips/',          hr_views.hr_payslips,          name='hr_payslips'),
    path('audit-logs/',        hr_views.hr_audit_logs,        name='hr_audit_logs'),
]
