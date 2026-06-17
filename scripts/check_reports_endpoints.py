"""Quick check: exercise report export endpoints using Django test client.
Creates a super-admin user (if missing) and force-authenticates the client.
Run with: DJANGO_SETTINGS_MODULE=worksphere.settings_check python scripts/check_reports_endpoints.py
"""
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path (script runs from scripts/)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'worksphere.settings_check')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

email = 'checkadmin@example.com'
password = 'testpassword123'

user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0], 'role': 'super_admin'})
if created:
    user.set_password(password)
    user.save()

client = Client()
client.force_login(user)

urls = [
    '/reports/attendance/export/csv/',
    '/reports/attendance/export/xlsx/',
    '/reports/attendance/export/pdf/',
]

for u in urls:
    resp = client.get(u)
    content_type = resp.get('Content-Type', '')
    print(f"GET {u} -> {resp.status_code} | Content-Type: {content_type} | Bytes: {len(resp.content) if hasattr(resp, 'content') else 'N/A'}")

sys.exit(0)
