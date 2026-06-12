from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(blank=True, max_length=150, unique=True)),
                ('role', models.CharField(choices=[
                    ('super_admin', 'Super Admin'), ('hr_admin', 'HR Admin'),
                    ('payroll_admin', 'Payroll Admin'), ('manager', 'Manager'),
                    ('employee', 'Employee'), ('auditor', 'Auditor'),
                ], default='employee', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_mfa_enabled', models.BooleanField(default=False)),
                ('mfa_secret', models.CharField(blank=True, max_length=32)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('password_changed_at', models.DateTimeField(blank=True, null=True)),
                ('must_change_password', models.BooleanField(default=False)),
                ('failed_login_attempts', models.PositiveIntegerField(default=0)),
                ('locked_until', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={'db_table': 'auth_users'},
        ),
        migrations.CreateModel(
            name='LoginHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_time', models.DateTimeField(auto_now_add=True)),
                ('logout_time', models.DateTimeField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('device_type', models.CharField(blank=True, max_length=50)),
                ('is_successful', models.BooleanField(default=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE,
                    related_name='login_history', to='authentication.user')),
            ],
            options={'db_table': 'auth_login_history', 'ordering': ['-login_time']},
        ),
        migrations.CreateModel(
            name='DeviceToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField()),
                ('platform', models.CharField(choices=[('android', 'Android'), ('ios', 'iOS'), ('web', 'Web')], max_length=10)),
                ('device_id', models.CharField(blank=True, max_length=255)),
                ('device_name', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE,
                    related_name='device_tokens', to='authentication.user')),
            ],
            options={'db_table': 'auth_device_tokens', 'unique_together': {('user', 'device_id')}},
        ),
    ]
