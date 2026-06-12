"""WorkSphere HR - Dashboard Views (Modern UI)"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET"])
def dashboard(request):
    """Modern dashboard view"""
    context = {
        'user': request.user,
    }
    return render(request, 'dashboard/modern_dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def employees_list(request):
    """Modern employees list view"""
    context = {
        'user': request.user,
    }
    return render(request, 'employees/modern_list.html', context)


@login_required
@require_http_methods(["GET"])
def attendance(request):
    """Modern attendance view"""
    context = {
        'user': request.user,
    }
    return render(request, 'attendance/modern_attendance.html', context)


@login_required
@require_http_methods(["GET"])
def leave_management(request):
    """Modern leave management view"""
    context = {
        'user': request.user,
    }
    return render(request, 'leave/modern_leave.html', context)


@login_required
@require_http_methods(["GET"])
def payroll(request):
    """Modern payroll view"""
    context = {
        'user': request.user,
    }
    return render(request, 'payroll/modern_payroll.html', context)


@login_required
@require_http_methods(["GET"])
def reports(request):
    """Modern reports view"""
    context = {
        'user': request.user,
    }
    return render(request, 'reports/modern_reports.html', context)
