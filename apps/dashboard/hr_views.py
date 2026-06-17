"""WorkSphere HR — HR Admin Views (departments, users, attendance mgmt, etc.)"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not getattr(request.user, 'is_admin_portal', False):
            raise PermissionDenied("You don't have permission to access admin pages.")
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def hr_departments(request):
    from apps.employees.models import Department
    departments = Department.objects.order_by('name')
    return render(request, 'hr/departments.html', {'departments': departments})


@admin_required
def hr_designations(request):
    from apps.employees.models import Designation
    designations = Designation.objects.select_related('department').order_by('department__name', 'name')
    return render(request, 'hr/designations.html', {'designations': designations})


@admin_required
def hr_locations(request):
    from apps.employees.models import Location
    locations = Location.objects.order_by('name')
    return render(request, 'hr/locations.html', {'locations': locations})


@admin_required
def hr_users(request):
    from apps.authentication.models import User
    search_q = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()
    qs = User.objects.order_by('email')
    if search_q:
        from django.db.models import Q
        qs = qs.filter(Q(email__icontains=search_q) | Q(first_name__icontains=search_q) | Q(last_name__icontains=search_q))
    if role_filter:
        qs = qs.filter(role=role_filter)
    return render(request, 'hr/users.html', {
        'users': qs[:200],
        'search_q': search_q,
        'role_filter': role_filter,
        'role_choices': User.ROLE_CHOICES,
    })


@admin_required
def hr_all_attendance(request):
    from apps.attendance.models import Attendance
    from apps.employees.models import Department
    today = timezone.now().date()
    date_from = request.GET.get('date_from', (today - timezone.timedelta(days=6)).isoformat())
    date_to = request.GET.get('date_to', today.isoformat())
    dept_id = request.GET.get('department', '')
    status_filter = request.GET.get('status', '')

    qs = Attendance.objects.select_related('employee', 'employee__department').order_by('-date', 'employee__first_name')
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    if dept_id:
        qs = qs.filter(employee__department_id=dept_id)
    if status_filter:
        qs = qs.filter(status=status_filter)

    return render(request, 'hr/all_attendance.html', {
        'records': list(qs[:500]),
        'total': qs.count(),
        'departments': Department.objects.filter(is_active=True).order_by('name'),
        'date_from': date_from,
        'date_to': date_to,
        'dept_id': dept_id,
        'status_filter': status_filter,
    })


@admin_required
def hr_all_leaves(request):
    from apps.leave_management.models import LeaveApplication
    from apps.employees.models import Department
    dept_id = request.GET.get('department', '')
    status_filter = request.GET.get('status', '')

    qs = LeaveApplication.objects.select_related('employee', 'employee__department', 'leave_type').order_by('-from_date')
    if dept_id:
        qs = qs.filter(employee__department_id=dept_id)
    if status_filter:
        qs = qs.filter(status=status_filter)

    return render(request, 'hr/all_leaves.html', {
        'applications': list(qs[:300]),
        'departments': Department.objects.filter(is_active=True).order_by('name'),
        'dept_id': dept_id,
        'status_filter': status_filter,
    })


@admin_required
def hr_regularization(request):
    from apps.attendance.models import AttendanceRegularization
    qs = AttendanceRegularization.objects.select_related('employee', 'employee__department').order_by('-created_at')[:200]
    return render(request, 'hr/regularization.html', {'requests': qs})


@admin_required
def hr_leave_types(request):
    from apps.leave_management.models import LeaveType
    leave_types = LeaveType.objects.order_by('name')
    return render(request, 'hr/leave_types.html', {'leave_types': leave_types})


@admin_required
def hr_salary_structures(request):
    try:
        from apps.payroll.models import SalaryStructure
        structures = SalaryStructure.objects.order_by('name')
    except Exception:
        structures = []
    return render(request, 'hr/salary_structures.html', {'structures': structures})


@admin_required
def hr_payslips(request):
    try:
        from apps.payroll.models import Payslip
        payslips = Payslip.objects.select_related('employee', 'payroll_run').order_by('-payroll_run__year', '-payroll_run__month')[:200]
    except Exception:
        payslips = []
    return render(request, 'hr/payslips.html', {'payslips': payslips})


@admin_required
def hr_audit_logs(request):
    try:
        from apps.audit.models import AuditLog
        logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:200]
    except Exception:
        logs = []
    return render(request, 'hr/audit_logs.html', {'logs': logs})
