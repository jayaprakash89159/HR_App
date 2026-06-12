"""
WorkSphere HR - Notifications Models
"""
from django.db import models
from django.conf import settings
import uuid


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('leave_request', 'Leave Request'),
        ('leave_approved', 'Leave Approved'),
        ('leave_rejected', 'Leave Rejected'),
        ('attendance_alert', 'Attendance Alert'),
        ('payslip', 'Payslip Generated'),
        ('birthday', 'Birthday'),
        ('anniversary', 'Work Anniversary'),
        ('document_expiry', 'Document Expiry'),
        ('general', 'General'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='notifications')
    notification_type = models.CharField(max_length=25, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hr_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user} - {self.title}"
