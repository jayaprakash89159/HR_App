"""WorkSphere HR - Notifications API URLs"""
from django.urls import path
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

@extend_schema(request=None, responses=None)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    from apps.notifications.models import Notification
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'count': count})

urlpatterns = [
    path('unread-count/', unread_count, name='unread_count'),
]
