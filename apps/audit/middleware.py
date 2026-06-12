"""
WorkSphere HR - Audit Middleware
Logs all significant user actions
"""
from django.utils import timezone
import json
import threading

_thread_locals = threading.local()


class AuditMiddleware:
    IGNORED_PATHS = ['/static/', '/media/', '/health/', '/favicon.ico']
    IGNORED_METHODS = ['GET', 'HEAD', 'OPTIONS']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only log writes for authenticated users
        if (request.user.is_authenticated and
                request.method not in self.IGNORED_METHODS and
                not any(request.path.startswith(p) for p in self.IGNORED_PATHS)):
            self._log(request, response)

        return response

    def _log(self, request, response):
        try:
            from apps.audit.models import AuditLog
            body = ''
            try:
                if hasattr(request, 'body') and request.body:
                    body_data = json.loads(request.body)
                    # Remove sensitive fields
                    for field in ['password', 'token', 'secret']:
                        body_data.pop(field, None)
                    body = json.dumps(body_data)[:1000]
            except Exception:
                pass

            AuditLog.objects.create(
                user=request.user,
                action=request.method,
                path=request.path[:500],
                ip_address=self._get_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                request_body=body,
                response_status=response.status_code,
            )
        except Exception:
            pass

    def _get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
