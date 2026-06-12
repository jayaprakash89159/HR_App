"""
WorkSphere HR - Celery Configuration
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'worksphere.settings')

app = Celery('worksphere')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'auto-punchout-midnight': {
        'task': 'apps.attendance.tasks.auto_punch_out',
        'schedule': crontab(hour=23, minute=59),
    },
    'birthday-notifications': {
        'task': 'apps.notifications.tasks.send_birthday_notifications',
        'schedule': crontab(hour=9, minute=0),
    },
    'anniversary-notifications': {
        'task': 'apps.notifications.tasks.send_anniversary_notifications',
        'schedule': crontab(hour=9, minute=30),
    },
    'cleanup-audit-logs': {
        'task': 'apps.audit.tasks.cleanup_old_logs',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
