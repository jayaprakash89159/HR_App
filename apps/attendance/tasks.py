"""WorkSphere HR - Attendance Celery Tasks"""
from celery import shared_task
from django.utils import timezone


@shared_task(name='apps.attendance.tasks.auto_punch_out')
def auto_punch_out():
    """Auto clock-out employees who forgot to clock out"""
    from apps.attendance.models import Attendance
    today = timezone.now().date()
    now = timezone.now()

    # Find records with clock-in but no clock-out for today
    pending = Attendance.objects.filter(
        date=today,
        clock_in__isnull=False,
        clock_out__isnull=True,
        status='present'
    )

    count = 0
    for record in pending:
        record.clock_out = now.replace(hour=23, minute=59, second=0)
        total_mins = int((record.clock_out - record.clock_in).total_seconds() / 60)
        record.total_working_minutes = max(0, total_mins)
        record.effective_working_minutes = max(0, total_mins - record.total_break_minutes)
        record.admin_remarks = 'Auto punched out by system at midnight'
        record.save(update_fields=['clock_out', 'total_working_minutes',
                                   'effective_working_minutes', 'admin_remarks'])
        count += 1

    return f'Auto punched out {count} employees'


@shared_task(name='apps.attendance.tasks.generate_daily_summary')
def generate_daily_summary():
    """Generate daily attendance summary"""
    from apps.attendance.models import Attendance
    from apps.employees.models import Employee
    today = timezone.now().date()

    # Mark absent for employees with no record today (weekday only)
    if today.weekday() < 5:  # Monday-Friday
        employees = Employee.objects.filter(status='active')
        created = 0
        for emp in employees:
            _, was_created = Attendance.objects.get_or_create(
                employee=emp,
                date=today,
                defaults={'status': 'absent'}
            )
            if was_created:
                created += 1
        return f'Generated {created} absent records for {today}'
    return f'{today} is a weekend, skipping'
