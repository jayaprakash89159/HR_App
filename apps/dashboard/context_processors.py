"""WorkSphere HR - Dashboard Context Processors"""
from django.conf import settings


def worksphere_settings(request):
    """Inject global settings into all templates"""
    try:
        ws = settings.WORKSPHERE
        ctx = {
            'COMPANY_NAME': ws.get('COMPANY_NAME', 'WorkSphere HR'),
            'COMPANY_LOGO': ws.get('COMPANY_LOGO', ''),
            'CURRENCY_SYMBOL': ws.get('CURRENCY_SYMBOL', '₹'),
        }
    except Exception:
        ctx = {
            'COMPANY_NAME': 'WorkSphere HR',
            'COMPANY_LOGO': '',
            'CURRENCY_SYMBOL': '₹',
        }

    # Pending approvals count for managers/HR
    if request.user.is_authenticated and (request.user.is_manager or request.user.is_hr_admin or request.user.is_super_admin):
        try:
            from apps.leave_management.models import LeaveApplication
            from apps.employees.models import Employee

            if request.user.is_hr_admin or request.user.is_super_admin:
                ctx['pending_leave_count'] = LeaveApplication.objects.filter(status='pending').count()
            else:
                try:
                    mgr_emp = request.user.employee_profile
                    if mgr_emp:
                        team_ids = Employee.objects.filter(reporting_manager=mgr_emp).values_list('id', flat=True)
                        ctx['pending_leave_count'] = LeaveApplication.objects.filter(
                            employee_id__in=team_ids, status='pending'
                        ).count()
                    else:
                        ctx['pending_leave_count'] = 0
                except Exception:
                    ctx['pending_leave_count'] = 0
        except Exception:
            ctx['pending_leave_count'] = 0
    else:
        ctx['pending_leave_count'] = 0

    return ctx
