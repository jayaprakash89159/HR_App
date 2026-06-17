"""
WorkSphere HR - Attendance Models
Complete attendance management with geo-fencing
"""
from django.db import models
from django.conf import settings
from apps.employees.models import Employee
import uuid


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('late_mark', 'Late Mark'),
        ('holiday', 'Holiday'),
        ('week_off', 'Week Off'),
        ('on_duty', 'On Duty'),
        ('work_from_home', 'Work From Home'),
        ('leave', 'Leave'),
        ('comp_off', 'Comp Off'),
        ('short_leave', 'Short Leave'),
    ]

    SOURCE_CHOICES = [
        ('web', 'Web'), ('mobile', 'Mobile'), ('biometric', 'Biometric'),
        ('qr', 'QR Code'), ('admin', 'Admin'), ('auto', 'Auto'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')

    # Clock times
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)

    # Break times
    break_in = models.DateTimeField(null=True, blank=True)
    break_out = models.DateTimeField(null=True, blank=True)
    total_break_minutes = models.PositiveIntegerField(default=0)

    # Hours
    total_working_minutes = models.PositiveIntegerField(default=0)
    effective_working_minutes = models.PositiveIntegerField(default=0)
    overtime_minutes = models.PositiveIntegerField(default=0)

    # Late/Early
    late_minutes = models.PositiveIntegerField(default=0)
    early_leaving_minutes = models.PositiveIntegerField(default=0)

    # Source
    clock_in_source = models.CharField(max_length=15, choices=SOURCE_CHOICES, blank=True)
    clock_out_source = models.CharField(max_length=15, choices=SOURCE_CHOICES, blank=True)

    # Location at clock in
    clock_in_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    clock_in_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    clock_in_address = models.TextField(blank=True)
    clock_in_within_geofence = models.BooleanField(null=True, blank=True)

    # Location at clock out
    clock_out_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    clock_out_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    clock_out_address = models.TextField(blank=True)
    clock_out_within_geofence = models.BooleanField(null=True, blank=True)

    # Selfie at clock in/out
    clock_in_selfie = models.ImageField(upload_to='attendance/selfies/', null=True, blank=True)
    clock_out_selfie = models.ImageField(upload_to='attendance/selfies/', null=True, blank=True)

    # Work from home
    is_wfh = models.BooleanField(default=False)
    wfh_approved = models.BooleanField(default=False)

    # Remarks
    remarks = models.TextField(blank=True)
    admin_remarks = models.TextField(blank=True)

    # Regularization
    is_regularized = models.BooleanField(default=False)
    regularized_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name='regularized_attendance')
    regularized_at = models.DateTimeField(null=True, blank=True)

    # Shift reference
    shift = models.ForeignKey('shifts.Shift', null=True, blank=True, on_delete=models.SET_NULL)

    # ── Approval workflow ──────────────────────────────────────
    # A punch (photo + GPS) only counts in reports once approved.
    # Until then it's 'pending' and visible only to the employee
    # themselves as their own "today" status.
    APPROVAL_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='approved_attendance')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_attendance'
        unique_together = ['employee', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'status']),
            models.Index(fields=['employee', '-date']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"

    def calculate_hours(self):
        if self.clock_in and self.clock_out:
            total = (self.clock_out - self.clock_in).total_seconds() / 60
            self.total_working_minutes = int(total)
            self.effective_working_minutes = int(total) - self.total_break_minutes
            self.save(update_fields=['total_working_minutes', 'effective_working_minutes'])

    @property
    def working_hours_display(self) -> str:
        minutes = self.effective_working_minutes
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"
    


class AttendanceRegularization(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('approved', 'Approved'),
        ('rejected', 'Rejected'), ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='regularizations')
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='regularizations')
    requested_clock_in = models.DateTimeField(null=True, blank=True)
    requested_clock_out = models.DateTimeField(null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                     on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hr_attendance_regularization'
        ordering = ['-created_at']


class ODApplication(models.Model):
    """On Duty Application"""
    OD_TYPE_CHOICES = [
        ('client_visit', 'Client Visit'),
        ('business_travel', 'Business Travel'),
        ('site_visit', 'Site Visit'),
        ('external_meeting', 'External Meeting'),
        ('training', 'Training'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('approved', 'Approved'),
        ('rejected', 'Rejected'), ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='od_applications')
    od_type = models.CharField(max_length=20, choices=OD_TYPE_CHOICES)
    from_date = models.DateField()
    to_date = models.DateField()
    from_time = models.TimeField(null=True, blank=True)
    to_time = models.TimeField(null=True, blank=True)
    total_days = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    client_name = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=300, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    # Approvals
    manager_approved = models.BooleanField(null=True, blank=True)
    manager_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                             on_delete=models.SET_NULL, related_name='od_manager_approvals')
    manager_approved_at = models.DateTimeField(null=True, blank=True)
    manager_remarks = models.TextField(blank=True)

    hr_approved = models.BooleanField(null=True, blank=True)
    hr_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name='od_hr_approvals')
    hr_approved_at = models.DateTimeField(null=True, blank=True)
    hr_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_od_applications'
        ordering = ['-created_at']


class ShortTimeOff(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('approved', 'Approved'),
        ('rejected', 'Rejected'), ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='short_time_offs')
    date = models.DateField()
    from_time = models.TimeField()
    to_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                     on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hr_short_time_off'
        ordering = ['-created_at']


class SwipeLog(models.Model):
    """Raw biometric/device swipe logs"""
    SWIPE_TYPE_CHOICES = [('in', 'In'), ('out', 'Out'), ('break_in', 'Break In'), ('break_out', 'Break Out')]
    SWIPE_SOURCE_CHOICES = [('biometric', 'Biometric'), ('mobile', 'Mobile'), ('web', 'Web'), ('qr', 'QR')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='swipe_logs')
    swipe_time = models.DateTimeField()
    swipe_type = models.CharField(max_length=10, choices=SWIPE_TYPE_CHOICES)
    source = models.CharField(max_length=15, choices=SWIPE_SOURCE_CHOICES)
    device_id = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hr_swipe_logs'
        ordering = ['-swipe_time']
        indexes = [
            models.Index(fields=['employee', 'swipe_time']),
        ]
