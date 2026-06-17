"""
WorkSphere HR - Authentication Models
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('hr_admin', 'HR Admin'),
        ('hr_executive', 'HR Executive'),
        ('payroll_admin', 'Payroll Admin'),
        ('finance', 'Finance'),
        ('manager', 'Manager'),
        ('reporting_manager', 'Reporting Manager'),
        ('project_manager', 'Project Manager'),
        ('employee', 'Employee'),
        ('auditor', 'Auditor'),
    ]

    EMPLOYEE_ROLES = {'employee', 'manager', 'reporting_manager', 'project_manager'}
    MANAGER_ROLES = {'manager', 'reporting_manager', 'project_manager'}
    HR_ROLES = {'super_admin', 'hr_admin', 'hr_executive'}
    PAYROLL_ROLES = {'super_admin', 'payroll_admin', 'finance'}
    REPORTING_ROLES = HR_ROLES | {'auditor', 'reporting_manager', 'finance', 'payroll_admin'}
    ADMIN_ROLES = HR_ROLES | PAYROLL_ROLES | {'auditor'}

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'auth_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)

    @property
    def is_locked(self):
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False

    @property
    def is_super_admin(self):
        return self.role == 'super_admin'

    @property
    def is_hr_admin(self):
        return self.role == 'hr_admin'

    @property
    def is_hr_executive(self):
        return self.role == 'hr_executive'

    @property
    def is_payroll_admin(self):
        return self.role == 'payroll_admin'

    @property
    def is_finance(self):
        return self.role == 'finance'

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_reporting_manager(self):
        return self.role == 'reporting_manager'

    @property
    def is_project_manager(self):
        return self.role == 'project_manager'

    @property
    def is_employee(self):
        return self.role == 'employee'

    @property
    def is_employee_portal(self):
        return self.role in self.EMPLOYEE_ROLES

    @property
    def is_hr_portal(self):
        return self.role in self.HR_ROLES or self.role == 'super_admin'

    @property
    def is_payroll_portal(self):
        return self.role in self.PAYROLL_ROLES or self.role == 'super_admin'

    @property
    def is_reporting_portal(self):
        return self.role in self.REPORTING_ROLES

    @property
    def is_admin_portal(self):
        return self.role in self.ADMIN_ROLES

    @property
    def can_access_reports(self):
        return self.role in self.REPORTING_ROLES or self.role in self.HR_ROLES or self.role == 'super_admin'

    @property
    def can_view_team_attendance(self):
        return self.role in self.MANAGER_ROLES or self.role in self.HR_ROLES or self.role == 'super_admin'

    @property
    def can_manage_users(self):
        return self.role in self.ADMIN_ROLES

    @property
    def can_manage_employees(self):
        return self.role in self.HR_ROLES or self.role == 'super_admin'

    @property
    def can_manage_payroll(self):
        return self.role in self.PAYROLL_ROLES or self.role == 'super_admin'

    @property
    def can_approve_leaves(self):
        return self.role in self.MANAGER_ROLES or self.role in self.HR_ROLES or self.role == 'super_admin'

    def has_role(self, *roles):
        return self.role in set(roles)


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history', null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_successful = models.BooleanField(default=True)

    class Meta:
        db_table = 'auth_login_history'
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.email} - {self.login_time}"


class DeviceToken(models.Model):
    PLATFORM_CHOICES = [('android', 'Android'), ('ios', 'iOS'), ('web', 'Web')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.TextField()
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    device_id = models.CharField(max_length=255, blank=True)
    device_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auth_device_tokens'
        unique_together = ['user', 'device_id']

    def __str__(self):
        return f"{self.user.email} - {self.platform}"
