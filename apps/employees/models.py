"""
WorkSphere HR - Employee Models
Complete employee data management
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    head = models.ForeignKey('Employee', null=True, blank=True, on_delete=models.SET_NULL,
                              related_name='headed_department')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='sub_departments')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_departments'
        ordering = ['name']

    def __str__(self):
        return self.name


class Designation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations')
    grade = models.CharField(max_length=20, blank=True)
    level = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_designations'
        ordering = ['department', 'level']

    def __str__(self):
        return f"{self.name} - {self.department.name}"


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    geo_fence_radius = models.PositiveIntegerField(default=200, help_text='Radius in meters')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_locations'

    def __str__(self):
        return f"{self.name} - {self.city}"


class CostCenter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_cost_centers'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Employee(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('P', 'Prefer not to say')]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'), ('married', 'Married'),
        ('divorced', 'Divorced'), ('widowed', 'Widowed'),
    ]
    EMPLOYMENT_TYPE_CHOICES = [
        ('permanent', 'Permanent'), ('contract', 'Contract'),
        ('intern', 'Intern'), ('consultant', 'Consultant'), ('probation', 'Probation'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'), ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'), ('resigned', 'Resigned'),
        ('terminated', 'Terminated'), ('absconding', 'Absconding'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='employee_profile', null=True, blank=True)

    # Identity
    employee_id = models.CharField(max_length=20, unique=True)
    employee_code = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='employees/photos/', null=True, blank=True)

    # Contact
    personal_email = models.EmailField(blank=True)
    official_email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    alternate_mobile = models.CharField(max_length=15, blank=True)

    # Personal
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, default='Indian')
    religion = models.CharField(max_length=100, blank=True)

    # Address
    current_address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10, blank=True)

    # Employment
    joining_date = models.DateField()
    confirmation_date = models.DateField(null=True, blank=True)
    probation_end_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='employees')
    reporting_manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                                           related_name='direct_reports')
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='employees')
    cost_center = models.ForeignKey(CostCenter, null=True, blank=True, on_delete=models.SET_NULL)
    employment_type = models.CharField(max_length=15, choices=EMPLOYMENT_TYPE_CHOICES, default='permanent')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')

    # Separation
    last_working_day = models.DateField(null=True, blank=True)
    separation_reason = models.TextField(blank=True)
    separation_type = models.CharField(max_length=50, blank=True)

    # System
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='created_employees')

    class Meta:
        db_table = 'hr_employees'
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['employee_code']),
            models.Index(fields=['official_email']),
            models.Index(fields=['department']),
            models.Index(fields=['status']),
            models.Index(fields=['joining_date']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_code})"

    def get_full_name(self):
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return ' '.join(parts)

    @property
    def age(self):
        today = timezone.now().date()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @property
    def years_of_service(self):
        today = timezone.now().date()
        joined = self.joining_date
        return today.year - joined.year - ((today.month, today.day) < (joined.month, joined.day))


class EmergencyContact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'), ('parent', 'Parent'), ('sibling', 'Sibling'),
        ('child', 'Child'), ('friend', 'Friend'), ('other', 'Other'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'hr_emergency_contacts'


class EmployeeBank(models.Model):
    ACCOUNT_TYPE_CHOICES = [('savings', 'Savings'), ('current', 'Current')]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='bank_accounts')
    bank_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=30)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='savings')
    ifsc_code = models.CharField(max_length=15)
    branch_name = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'hr_employee_banks'


class EmployeeStatutory(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='statutory')
    pan_number = models.CharField(max_length=10, blank=True)
    aadhaar_number = models.CharField(max_length=12, blank=True)
    uan_number = models.CharField(max_length=12, blank=True)
    pf_number = models.CharField(max_length=22, blank=True)
    esi_number = models.CharField(max_length=17, blank=True)
    pt_number = models.CharField(max_length=20, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    passport_expiry = models.DateField(null=True, blank=True)
    driving_license_number = models.CharField(max_length=20, blank=True)
    driving_license_expiry = models.DateField(null=True, blank=True)
    is_pf_applicable = models.BooleanField(default=True)
    is_esi_applicable = models.BooleanField(default=True)
    is_pt_applicable = models.BooleanField(default=True)
    pf_contribution_type = models.CharField(max_length=20, default='statutory',
                                             choices=[('statutory', 'Statutory'), ('voluntary', 'Voluntary')])

    class Meta:
        db_table = 'hr_employee_statutory'


class EmployeeFamily(models.Model):
    RELATION_CHOICES = [
        ('spouse', 'Spouse'), ('child', 'Child'), ('parent', 'Parent'),
        ('sibling', 'Sibling'), ('other', 'Other'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='family_members')
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=20, choices=RELATION_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    is_nominee = models.BooleanField(default=False)
    nominee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_dependent = models.BooleanField(default=False)

    class Meta:
        db_table = 'hr_employee_family'


class EmployeeEducation(models.Model):
    DEGREE_CHOICES = [
        ('10th', '10th Standard'), ('12th', '12th Standard'),
        ('diploma', 'Diploma'), ('bachelor', "Bachelor's"),
        ('master', "Master's"), ('phd', 'PhD'), ('other', 'Other'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES)
    institution = models.CharField(max_length=300)
    field_of_study = models.CharField(max_length=200)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)
    grade = models.CharField(max_length=20, blank=True)
    is_highest = models.BooleanField(default=False)

    class Meta:
        db_table = 'hr_employee_education'
        ordering = ['-end_year']


class EmployeeExperience(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='experience')
    company_name = models.CharField(max_length=300)
    designation = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    reason_for_leaving = models.TextField(blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'hr_employee_experience'
        ordering = ['-start_date']


class EmployeeSkill(models.Model):
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'), ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'), ('expert', 'Expert'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=200)
    proficiency = models.CharField(max_length=15, choices=PROFICIENCY_CHOICES)
    years_of_experience = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'hr_employee_skills'
