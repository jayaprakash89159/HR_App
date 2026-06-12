"""WorkSphere HR - Dashboard API URLs"""
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    from apps.attendance.models import Attendance
    from apps.leave_management.models import LeaveApplication
    today = timezone.now().date()
    try:
        emp = request.user.employee_profile
        today_att = Attendance.objects.filter(employee=emp, date=today).first()
        return Response({
            'today_status': today_att.status if today_att else 'not_marked',
            'clock_in': today_att.clock_in.isoformat() if today_att and today_att.clock_in else None,
            'clock_out': today_att.clock_out.isoformat() if today_att and today_att.clock_out else None,
        })
    except Exception:
        return Response({'error': 'No employee profile'}, status=400)

urlpatterns = [
    path('stats/', dashboard_stats, name='dashboard_stats'),
]
