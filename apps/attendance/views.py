"""
WorkSphere HR - Attendance API Views
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import math

from apps.attendance.models import (
    Attendance, AttendanceRegularization, ODApplication, ShortTimeOff, SwipeLog
)
from apps.employees.models import Employee


class ClockInView(APIView):
    """Mobile and Web clock-in with GPS and selfie"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            employee = request.user.employee_profile
        except Exception:
            return Response({'error': 'Employee profile not found'}, status=400)

        today = timezone.now().date()
        now = timezone.now()

        # Check if already clocked in today
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={'status': 'present'}
        )

        if attendance.clock_in and not created:
            return Response({'error': 'Already clocked in for today'}, status=400)

        # Extract location data
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        address = request.data.get('address', '')
        source = request.data.get('source', 'mobile')

        # Geo-fence validation
        within_geofence = None
        if latitude and longitude and employee.location:
            within_geofence = self._check_geofence(
                float(latitude), float(longitude),
                employee.location
            )

        # Update attendance
        attendance.clock_in = now
        attendance.clock_in_source = source
        attendance.clock_in_latitude = latitude
        attendance.clock_in_longitude = longitude
        attendance.clock_in_address = address
        attendance.clock_in_within_geofence = within_geofence
        attendance.status = 'present'

        # Handle selfie upload
        if 'selfie' in request.FILES:
            attendance.clock_in_selfie = request.FILES['selfie']

        # Calculate late minutes
        if employee.shift_assignments.filter(is_active=True).exists():
            shift = employee.shift_assignments.filter(is_active=True).first().shift
            shift_start = datetime.combine(today, shift.start_time)
            shift_start = timezone.make_aware(shift_start)
            grace = timezone.timedelta(minutes=shift.grace_period_minutes)

            if now > (shift_start + grace):
                late_mins = int((now - shift_start).total_seconds() / 60)
                attendance.late_minutes = max(0, late_mins - shift.grace_period_minutes)
                if attendance.late_minutes > 0:
                    attendance.status = 'late_mark'

        attendance.save()

        # Create swipe log
        SwipeLog.objects.create(
            employee=employee,
            swipe_time=now,
            swipe_type='in',
            source=source,
            latitude=latitude,
            longitude=longitude,
            is_processed=True,
        )

        return Response({
            'success': True,
            'message': 'Clocked in successfully',
            'clock_in': attendance.clock_in.isoformat(),
            'within_geofence': within_geofence,
            'late_minutes': attendance.late_minutes,
            'status': attendance.status,
        })

    def _check_geofence(self, lat, lon, location):
        if not location.latitude or not location.longitude:
            return None

        # Haversine formula
        R = 6371000  # Earth's radius in meters
        lat1 = math.radians(float(location.latitude))
        lat2 = math.radians(lat)
        delta_lat = math.radians(lat - float(location.latitude))
        delta_lon = math.radians(lon - float(location.longitude))

        a = (math.sin(delta_lat/2) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon/2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c

        return distance <= location.geo_fence_radius


class ClockOutView(APIView):
    """Clock out with GPS"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            employee = request.user.employee_profile
        except Exception:
            return Response({'error': 'Employee profile not found'}, status=400)

        today = timezone.now().date()
        now = timezone.now()

        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response({'error': 'No attendance record found for today'}, status=400)

        if not attendance.clock_in:
            return Response({'error': 'You have not clocked in yet'}, status=400)

        if attendance.clock_out:
            return Response({'error': 'Already clocked out for today'}, status=400)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        address = request.data.get('address', '')
        source = request.data.get('source', 'mobile')

        within_geofence = None
        if latitude and longitude and employee.location:
            within_geofence = ClockInView()._check_geofence(
                float(latitude), float(longitude), employee.location
            )

        attendance.clock_out = now
        attendance.clock_out_source = source
        attendance.clock_out_latitude = latitude
        attendance.clock_out_longitude = longitude
        attendance.clock_out_address = address
        attendance.clock_out_within_geofence = within_geofence

        if 'selfie' in request.FILES:
            attendance.clock_out_selfie = request.FILES['selfie']

        # Calculate working hours
        total_mins = int((now - attendance.clock_in).total_seconds() / 60)
        attendance.total_working_minutes = total_mins
        attendance.effective_working_minutes = total_mins - attendance.total_break_minutes

        # Check if half day
        if employee.shift_assignments.filter(is_active=True).exists():
            shift = employee.shift_assignments.filter(is_active=True).first().shift
            half_day_mins = float(shift.minimum_hours) * 60
            full_day_mins = float(shift.full_day_hours) * 60
            if attendance.effective_working_minutes < half_day_mins:
                attendance.status = 'absent'
            elif attendance.effective_working_minutes < full_day_mins:
                attendance.status = 'half_day'

            # Calculate overtime
            if attendance.effective_working_minutes > full_day_mins:
                attendance.overtime_minutes = attendance.effective_working_minutes - int(full_day_mins)

        attendance.save()

        SwipeLog.objects.create(
            employee=employee,
            swipe_time=now,
            swipe_type='out',
            source=source,
            latitude=latitude,
            longitude=longitude,
            is_processed=True,
        )

        return Response({
            'success': True,
            'message': 'Clocked out successfully',
            'clock_out': attendance.clock_out.isoformat(),
            'working_hours': attendance.working_hours_display,
            'total_working_minutes': attendance.total_working_minutes,
            'overtime_minutes': attendance.overtime_minutes,
        })


class AttendanceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.select_related('employee', 'shift')

        if user.role == 'employee':
            try:
                qs = qs.filter(employee=user.employee_profile)
            except Exception:
                return Attendance.objects.none()
        elif user.role == 'manager':
            try:
                manager_emp = user.employee_profile
                team_ids = Employee.objects.filter(
                    reporting_manager=manager_emp
                ).values_list('id', flat=True)
                qs = qs.filter(employee_id__in=team_ids)
            except Exception:
                return Attendance.objects.none()

        # Date filters
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        employee_id = self.request.query_params.get('employee_id')
        status_filter = self.request.query_params.get('status')

        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs.order_by('-date')

    def get_serializer_class(self):
        from apps.attendance.serializers import AttendanceSerializer
        return AttendanceSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's attendance for current user"""
        try:
            employee = request.user.employee_profile
            today = timezone.now().date()
            attendance = Attendance.objects.filter(employee=employee, date=today).first()
            if attendance:
                from apps.attendance.serializers import AttendanceSerializer
                return Response(AttendanceSerializer(attendance).data)
            return Response({'date': str(today), 'status': 'not_marked', 'clock_in': None, 'clock_out': None})
        except Exception:
            return Response({'error': 'Profile not found'}, status=400)

    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """Monthly attendance summary"""
        try:
            employee = request.user.employee_profile
        except Exception:
            return Response({'error': 'Profile not found'}, status=400)

        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))

        records = Attendance.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month
        )

        from collections import Counter
        status_counts = Counter(records.values_list('status', flat=True))

        total_working_mins = sum(r.effective_working_minutes for r in records)
        total_overtime_mins = sum(r.overtime_minutes for r in records)

        return Response({
            'year': year,
            'month': month,
            'total_days': records.count(),
            'present': status_counts.get('present', 0),
            'absent': status_counts.get('absent', 0),
            'half_day': status_counts.get('half_day', 0),
            'late_mark': status_counts.get('late_mark', 0),
            'on_duty': status_counts.get('on_duty', 0),
            'work_from_home': status_counts.get('work_from_home', 0),
            'leave': status_counts.get('leave', 0),
            'holiday': status_counts.get('holiday', 0),
            'total_working_hours': f"{total_working_mins // 60}h {total_working_mins % 60}m",
            'total_overtime_hours': f"{total_overtime_mins // 60}h {total_overtime_mins % 60}m",
        })
