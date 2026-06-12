"""
WorkSphere HR - Authentication API Views
JWT-based authentication endpoints
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone

from apps.authentication.models import LoginHistory, DeviceToken


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        device_token = request.data.get('device_token')
        platform = request.data.get('platform', 'mobile')

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=400)

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({'error': 'Invalid credentials'}, status=401)

        if not user.is_active:
            return Response({'error': 'Account deactivated'}, status=403)

        if user.is_locked:
            return Response({'error': 'Account temporarily locked'}, status=403)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Save device token for push notifications
        if device_token:
            DeviceToken.objects.update_or_create(
                user=user,
                device_id=request.data.get('device_id', device_token[:50]),
                defaults={'token': device_token, 'platform': platform, 'is_active': True}
            )

        # Log login
        try:
            LoginHistory.objects.create(
                user=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                device_type=platform,
                is_successful=True,
            )
        except Exception:
            pass  # Continue even if logging fails

        # Build user data
        user_data = {
            'id': str(user.id),
            'email': user.email,
            'role': user.role,
        }

        try:
            emp = user.employee_profile
            user_data.update({
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'employee_code': emp.employee_code,
                'designation': emp.designation.name,
                'department': emp.department.name,
                'profile_photo': request.build_absolute_uri(emp.profile_photo.url) if emp.profile_photo else None,
            })
        except Exception:
            user_data.update({'first_name': '', 'last_name': ''})

        return Response({
            'access': str(access),
            'refresh': str(refresh),
            'user': user_data,
        })


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            # Deactivate device token
            device_id = request.data.get('device_id')
            if device_id:
                DeviceToken.objects.filter(user=request.user, device_id=device_id).update(is_active=False)

            # Update logout time
            LoginHistory.objects.filter(
                user=request.user, logout_time__isnull=True
            ).update(logout_time=timezone.now())

        except Exception:
            pass

        return Response({'message': 'Logged out successfully'})


class UserProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': str(user.id),
            'email': user.email,
            'role': user.role,
            'is_mfa_enabled': user.is_mfa_enabled,
        }

        try:
            emp = user.employee_profile
            data.update({
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'full_name': emp.get_full_name(),
                'employee_code': emp.employee_code,
                'mobile': emp.mobile,
                'designation': emp.designation.name,
                'department': emp.department.name,
                'location': emp.location.name,
                'joining_date': str(emp.joining_date),
                'profile_photo': request.build_absolute_uri(emp.profile_photo.url) if emp.profile_photo else None,
            })
        except Exception:
            pass

        return Response(data)
