from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

EMPLOYEE_PORTAL_ROLES = {'employee', 'manager', 'reporting_manager', 'project_manager'}
MANAGER_PORTAL_ROLES = {'manager', 'reporting_manager', 'project_manager'}
HR_PORTAL_ROLES = {'super_admin', 'hr_admin', 'hr_executive'}
PAYROLL_PORTAL_ROLES = {'super_admin', 'payroll_admin', 'finance'}
REPORTING_PORTAL_ROLES = HR_PORTAL_ROLES | {'auditor', 'reporting_manager', 'finance', 'payroll_admin'}
ADMIN_PORTAL_ROLES = HR_PORTAL_ROLES | PAYROLL_PORTAL_ROLES | {'auditor'}
MANAGER_OR_HR_ROLES = MANAGER_PORTAL_ROLES | HR_PORTAL_ROLES


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_role(*allowed_roles):
                return redirect('/')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def employee_portal_only(view_func):
    return role_required(EMPLOYEE_PORTAL_ROLES)(view_func)


def hr_portal_only(view_func):
    return role_required(HR_PORTAL_ROLES)(view_func)


def payroll_portal_only(view_func):
    return role_required(PAYROLL_PORTAL_ROLES)(view_func)


def reporting_portal_only(view_func):
    return role_required(REPORTING_PORTAL_ROLES)(view_func)


def manager_portal_only(view_func):
    return role_required(MANAGER_PORTAL_ROLES)(view_func)


def manager_or_hr_portal_only(view_func):
    return role_required(MANAGER_OR_HR_ROLES)(view_func)


def admin_portal_only(view_func):
    return role_required(ADMIN_PORTAL_ROLES)(view_func)
