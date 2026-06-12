"""WorkSphere HR - Audit Tasks"""
from celery import shared_task
from django.utils import timezone


@shared_task(name='apps.audit.tasks.cleanup_old_logs')
def cleanup_old_logs():
    from apps.audit.models import AuditLog
    cutoff = timezone.now() - timezone.timedelta(days=90)
    deleted, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
    return f'Deleted {deleted} old audit logs'
