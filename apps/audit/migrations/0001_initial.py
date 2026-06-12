from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('authentication', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('action', models.CharField(max_length=10)),
                ('path', models.CharField(max_length=500)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('request_body', models.TextField(blank=True)),
                ('response_status', models.PositiveIntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='audit_logs', to='authentication.user')),
            ],
            options={'db_table': 'hr_audit_logs', 'ordering': ['-created_at']},
        ),
    ]
