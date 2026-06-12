"""
WorkSphere HR - Shift Management Models
"""
from django.db import models
from django.conf import settings
from apps.employees.models import Employee
import uuid


class Shift(models.Model):
    SHIFT_TYPE_CHOICES = [
        ('general', 'General'), ('morning', 'Morning'), ('evening', 'Evening'),
        ('night', 'Night'), ('rotational', 'Rotational'), ('flexible', 'Flexible'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    shift_type = models.CharField(max_length=15, choices=SHIFT_TYPE_CHOICES, default='general')
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_period_minutes = models.PositiveIntegerField(default=15)
    early_cutoff_minutes = models.PositiveIntegerField(default=30)
    late_cutoff_minutes = models.PositiveIntegerField(default=120)
    minimum_hours = models.DecimalField(max_digits=4, decimal_places=2, default=4)
    full_day_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8)
    is_night_shift = models.BooleanField(default=False)
    working_days = models.JSONField(default=list, help_text='List of working day numbers (0=Mon, 6=Sun)')
    week_off_days = models.JSONField(default=list, help_text='Week off day numbers')
    color = models.CharField(max_length=7, default='#2563EB')
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'hr_shifts'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.start_time} - {self.end_time})"


class EmployeeShiftAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='shift_assignments')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='assignments')
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hr_shift_assignments'
        ordering = ['-effective_from']


class ShiftChangeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('approved', 'Approved'),
        ('rejected', 'Rejected'), ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='shift_change_requests')
    current_shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='outgoing_changes')
    requested_shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='incoming_changes')
    from_date = models.DateField()
    to_date = models.DateField(null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    manager_approved = models.BooleanField(null=True, blank=True)
    manager_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                             on_delete=models.SET_NULL, related_name='shift_manager_approvals')
    manager_approved_at = models.DateTimeField(null=True, blank=True)
    manager_remarks = models.TextField(blank=True)

    hr_approved = models.BooleanField(null=True, blank=True)
    hr_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name='shift_hr_approvals')
    hr_approved_at = models.DateTimeField(null=True, blank=True)
    hr_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_shift_change_requests'
        ordering = ['-created_at']
