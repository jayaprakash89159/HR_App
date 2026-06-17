from django.contrib import admin

from apps.employees.models import (
    CostCenter,
    Department,
    Designation,
    Employee,
    EmployeeBank,
    EmployeeEducation,
    EmployeeExperience,
    EmployeeFamily,
    EmployeeStatutory,
    EmergencyContact,
    Location,
    EmployeeSkill,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('is_active',)


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'grade', 'level')
    search_fields = ('name',)
    list_filter = ('department',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'state', 'country', 'is_active')
    search_fields = ('name', 'code', 'city', 'state')
    list_filter = ('country', 'is_active')


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('is_active',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_code', 'official_email', 'first_name', 'last_name',
        'department', 'designation', 'status', 'joining_date'
    )
    search_fields = ('employee_code', 'official_email', 'first_name', 'last_name')
    list_filter = ('department', 'designation', 'status', 'location')
    raw_id_fields = ('user', 'reporting_manager', 'location', 'department', 'designation', 'cost_center')
    date_hierarchy = 'joining_date'
    ordering = ('employee_code',)


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('employee', 'name', 'relationship', 'phone', 'is_primary')
    search_fields = ('employee__employee_code', 'name', 'phone')
    list_filter = ('relationship', 'is_primary')


@admin.register(EmployeeBank)
class EmployeeBankAdmin(admin.ModelAdmin):
    list_display = ('employee', 'bank_name', 'account_number', 'is_primary', 'is_verified')
    search_fields = ('employee__employee_code', 'bank_name', 'account_number')
    list_filter = ('is_primary', 'is_verified')


admin.site.register(EmployeeStatutory)
admin.site.register(EmployeeFamily)
admin.site.register(EmployeeEducation)
admin.site.register(EmployeeExperience)
admin.site.register(EmployeeSkill)
