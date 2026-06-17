from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='approval_status',
            field=models.CharField(
                choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                default='pending',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='attendance',
            name='approved_by',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='approved_attendance',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='attendance',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='approval_remarks',
            field=models.TextField(blank=True),
        ),
        # Existing rows pre-date this workflow — treat them as already approved
        # so historical data isn't hidden from reports.
        migrations.RunSQL(
            sql="UPDATE hr_attendance SET approval_status = 'approved' WHERE approval_status = 'pending';",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
