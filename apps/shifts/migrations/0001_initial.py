from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('employees', '0001_initial'),
        ('authentication', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('shift_type', models.CharField(default='general', max_length=15)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('grace_period_minutes', models.PositiveIntegerField(default=15)),
                ('early_cutoff_minutes', models.PositiveIntegerField(default=30)),
                ('late_cutoff_minutes', models.PositiveIntegerField(default=120)),
                ('minimum_hours', models.DecimalField(decimal_places=2, default=4, max_digits=4)),
                ('full_day_hours', models.DecimalField(decimal_places=2, default=8, max_digits=4)),
                ('is_night_shift', models.BooleanField(default=False)),
                ('working_days', models.JSONField(default=list)),
                ('week_off_days', models.JSONField(default=list)),
                ('color', models.CharField(default='#2563EB', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={'db_table': 'hr_shifts', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='EmployeeShiftAssignment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('effective_from', models.DateField()),
                ('effective_to', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                    to='authentication.user')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='shift_assignments', to='employees.employee')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='assignments', to='shifts.shift')),
            ],
            options={'db_table': 'hr_shift_assignments', 'ordering': ['-effective_from']},
        ),
        migrations.CreateModel(
            name='ShiftChangeRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('from_date', models.DateField()),
                ('to_date', models.DateField(blank=True, null=True)),
                ('reason', models.TextField()),
                ('status', models.CharField(default='pending', max_length=15)),
                ('manager_approved', models.BooleanField(blank=True, null=True)),
                ('manager_approved_at', models.DateTimeField(blank=True, null=True)),
                ('manager_remarks', models.TextField(blank=True)),
                ('hr_approved', models.BooleanField(blank=True, null=True)),
                ('hr_approved_at', models.DateTimeField(blank=True, null=True)),
                ('hr_remarks', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='outgoing_changes', to='shifts.shift')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='shift_change_requests', to='employees.employee')),
                ('hr_approved_by', models.ForeignKey(blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='shift_hr_approvals', to='authentication.user')),
                ('manager_approved_by', models.ForeignKey(blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='shift_manager_approvals', to='authentication.user')),
                ('requested_shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='incoming_changes', to='shifts.shift')),
            ],
            options={'db_table': 'hr_shift_change_requests', 'ordering': ['-created_at']},
        ),
    ]
