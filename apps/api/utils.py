"""
WorkSphere HR - API Utilities
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.http import JsonResponse


def custom_exception_handler(exc, context):
    """Custom DRF exception handler with consistent response format"""
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'error': None,
            'errors': None,
        }

        if isinstance(response.data, dict):
            if 'detail' in response.data:
                error_data['error'] = str(response.data['detail'])
            else:
                error_data['errors'] = response.data
                # Extract first error message
                for key, value in response.data.items():
                    if isinstance(value, list):
                        error_data['error'] = f"{key}: {value[0]}"
                    else:
                        error_data['error'] = str(value)
                    break
        elif isinstance(response.data, list):
            error_data['error'] = str(response.data[0])
        else:
            error_data['error'] = str(response.data)

        response.data = error_data

    return response


def health_check(request):
    """Simple health check endpoint"""
    from django.db import connection
    from django.core.cache import cache

    checks = {'status': 'ok', 'database': 'ok', 'cache': 'ok'}

    try:
        connection.ensure_connection()
    except Exception:
        checks['database'] = 'error'
        checks['status'] = 'degraded'

    try:
        cache.set('health_check', '1', 5)
        cache.get('health_check')
    except Exception:
        checks['cache'] = 'error'
        checks['status'] = 'degraded'

    status_code = 200 if checks['status'] == 'ok' else 503
    return JsonResponse(checks, status=status_code)
