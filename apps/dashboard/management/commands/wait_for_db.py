"""
WorkSphere HR - wait_for_db management command
Waits for PostgreSQL to become available before proceeding
"""
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Wait for database to become available'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout', type=int, default=120,
            help='Maximum seconds to wait (default: 120)'
        )
        parser.add_argument(
            '--interval', type=int, default=2,
            help='Seconds between retries (default: 2)'
        )

    def handle(self, *args, **options):
        timeout = options['timeout']
        interval = options['interval']
        elapsed = 0

        self.stdout.write('⏳ Waiting for database...')

        while elapsed < timeout:
            try:
                conn = connections['default']
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS('✅ Database is ready!'))
                return
            except OperationalError as e:
                self.stdout.write(
                    f'   Database not ready ({elapsed}s elapsed): {e}'
                )
                time.sleep(interval)
                elapsed += interval

        self.stdout.write(
            self.style.ERROR(f'❌ Database did not become available after {timeout}s')
        )
        raise SystemExit(1)
