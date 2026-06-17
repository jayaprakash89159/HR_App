from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.authentication.models import DeviceToken, LoginHistory, User


@admin.register(User)
class WorkSphereUserAdmin(DjangoUserAdmin):
    model = User
    list_display = (
        'email', 'username', 'role', 'is_staff', 'is_superuser',
        'is_active', 'last_login', 'date_joined'
    )
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Security', {'fields': ('is_mfa_enabled', 'must_change_password', 'failed_login_attempts', 'locked_until', 'last_login_ip', 'password_changed_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_superuser'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'ip_address', 'is_successful')
    list_filter = ('is_successful', 'login_time')
    search_fields = ('user__email', 'ip_address', 'user_agent')
    date_hierarchy = 'login_time'
    readonly_fields = ('login_time', 'logout_time')


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'device_name', 'device_id', 'is_active', 'last_used')
    list_filter = ('platform', 'is_active')
    search_fields = ('user__email', 'device_name', 'device_id')
    readonly_fields = ('created_at', 'last_used')
