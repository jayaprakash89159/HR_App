"""
WorkSphere HR - Notification Tasks
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


@shared_task(name='apps.notifications.tasks.send_birthday_notifications')
def send_birthday_notifications():
    from apps.employees.models import Employee
    from apps.notifications.models import Notification

    today = timezone.now().date()
    birthdays = Employee.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
        status='active'
    ).select_related('user')

    for emp in birthdays:
        if emp.user:
            Notification.objects.create(
                user=emp.user,
                notification_type='birthday',
                title='🎂 Happy Birthday!',
                message=f'Wishing you a very Happy Birthday, {emp.first_name}! '
                        f'May this year bring you joy and success.'
            )

    return f'Sent {birthdays.count()} birthday notifications'


@shared_task(name='apps.notifications.tasks.send_anniversary_notifications')
def send_anniversary_notifications():
    from apps.employees.models import Employee
    from apps.notifications.models import Notification

    today = timezone.now().date()
    anniversaries = Employee.objects.filter(
        joining_date__month=today.month,
        joining_date__day=today.day,
        status='active'
    ).select_related('user')

    for emp in anniversaries:
        years = today.year - emp.joining_date.year
        if years > 0 and emp.user:
            Notification.objects.create(
                user=emp.user,
                notification_type='anniversary',
                title=f'🎉 {years} Year Work Anniversary!',
                message=f'Congratulations on completing {years} year{"s" if years > 1 else ""} '
                        f'with us, {emp.first_name}! Thank you for your dedication.'
            )

    return f'Sent {anniversaries.count()} anniversary notifications'


@shared_task(name='apps.notifications.tasks.send_password_reset_email')
def send_password_reset_email(user_id):
    from apps.authentication.models import User
    import secrets

    try:
        user = User.objects.get(id=user_id)
        token = secrets.token_urlsafe(32)
        # Store token in cache
        from django.core.cache import cache
        cache.set(f'password_reset_{token}', str(user.id), timeout=3600)

        reset_url = f"{settings.WORKSPHERE.get('COMPANY_WEBSITE', 'http://localhost:8000')}/auth/reset-password/{token}/"

        send_mail(
            subject='WorkSphere HR - Password Reset Request',
            message=f'Click the link below to reset your password:\n\n{reset_url}\n\nThis link expires in 1 hour.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as e:
        return f'Error: {e}'

    return f'Password reset email sent to {user.email}'


@shared_task(name='apps.notifications.tasks.notify_leave_status')
def notify_leave_status(leave_id, status):
    from apps.leave_management.models import LeaveApplication
    from apps.notifications.models import Notification

    try:
        leave = LeaveApplication.objects.select_related(
            'employee__user', 'leave_type'
        ).get(id=leave_id)

        if leave.employee.user:
            if status == 'approved':
                Notification.objects.create(
                    user=leave.employee.user,
                    notification_type='leave_approved',
                    title='✅ Leave Approved',
                    message=f'Your {leave.leave_type.name} from {leave.from_date} to {leave.to_date} has been approved.',
                    link=f'/leave/my-leaves/{leave.id}/'
                )
            elif status == 'rejected':
                Notification.objects.create(
                    user=leave.employee.user,
                    notification_type='leave_rejected',
                    title='❌ Leave Rejected',
                    message=f'Your {leave.leave_type.name} request has been rejected.',
                    link=f'/leave/my-leaves/{leave.id}/'
                )
    except Exception as e:
        return f'Error: {e}'
