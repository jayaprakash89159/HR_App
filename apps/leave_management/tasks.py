"""WorkSphere HR - Leave Management Celery Tasks"""
from celery import shared_task


@shared_task(name='apps.leave_management.tasks.monthly_leave_accrual')
def monthly_leave_accrual():
    """Accrue monthly leave for all active employees"""
    from apps.employees.models import Employee
    from apps.leave_management.models import LeaveType, LeaveBalance
    from django.utils import timezone

    today = timezone.now().date()
    year = today.year

    accrual_types = LeaveType.objects.filter(
        accrual_type='monthly', is_active=True
    )
    count = 0
    for lt in accrual_types:
        monthly_days = float(lt.days_allowed_per_year) / 12
        for emp in Employee.objects.filter(status='active'):
            balance, _ = LeaveBalance.objects.get_or_create(
                employee=emp, leave_type=lt, year=year,
                defaults={'entitled_days': lt.days_allowed_per_year}
            )
            balance.accrued = round(float(balance.accrued) + monthly_days, 2)
            balance.save(update_fields=['accrued'])
            count += 1

    return f'Accrued leave for {count} employee-leave combinations'
