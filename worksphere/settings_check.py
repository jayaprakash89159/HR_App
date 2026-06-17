"""
Temporary settings override for local `manage.py check` runs.
Uses SQLite to avoid requiring PostgreSQL client libraries during static checks.
Do NOT use this in production.
"""
from .settings import *

# Override DATABASES to use SQLite for quick local checks
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Allow Django test client host
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# For deploy checks we set recommended secure settings (this override is only for local checks)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Help drf-spectacular with enum naming (tweak if specific enum names differ)
SPECTACULAR_SETTINGS = globals().get('SPECTACULAR_SETTINGS', {})
SPECTACULAR_SETTINGS.setdefault('ENUM_NAME_OVERRIDES', {})
# Map duplicate choice constants to a single enum name to avoid multiple names for same choice set
SPECTACULAR_SETTINGS['ENUM_NAME_OVERRIDES'].setdefault('apps.attendance.models.Attendance.SOURCE_CHOICES', 'ClockSourceEnum')
SPECTACULAR_SETTINGS['ENUM_NAME_OVERRIDES'].setdefault('apps.attendance.models.SwipeLog.SWIPE_SOURCE_CHOICES', 'ClockSourceEnum')
