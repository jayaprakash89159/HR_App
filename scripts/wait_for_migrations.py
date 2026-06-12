#!/usr/bin/env python3
"""
Wait until Django migrations are fully complete.
Polls until django_celery_beat_periodictask table exists.
"""
import os
import sys
import time
import psycopg2

DB_HOST = os.environ.get('DB_HOST', 'postgres')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'worksphere_hr')
DB_USER = os.environ.get('DB_USER', 'worksphere')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'worksphere123')

MAX_WAIT = 300  # 5 minutes
INTERVAL = 5

print(f"⏳ Waiting for migrations to complete (max {MAX_WAIT}s)...")
elapsed = 0

while elapsed < MAX_WAIT:
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user=DB_USER, password=DB_PASSWORD, connect_timeout=5
        )
        cur = conn.cursor()
        # Check the table that celery-beat needs
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'django_celery_beat_periodictask'
            );
        """)
        exists = cur.fetchone()[0]
        cur.close()
        conn.close()

        if exists:
            print(f"✅ Migrations complete! django_celery_beat_periodictask table found.")
            sys.exit(0)
        else:
            print(f"   Table not ready yet ({elapsed}s elapsed)...")
    except Exception as e:
        print(f"   DB not ready ({elapsed}s): {e}")

    time.sleep(INTERVAL)
    elapsed += INTERVAL

print(f"❌ Migrations did not complete after {MAX_WAIT}s")
sys.exit(1)
