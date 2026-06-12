"""
WorkSphere HR - Authentication Views
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta

from apps.authentication.models import LoginHistory


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'auth/login.html')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated. Contact HR.')
                return render(request, 'auth/login.html')

            if user.is_locked:
                messages.error(request, f'Account temporarily locked. Try after {user.locked_until.strftime("%H:%M")}.')
                return render(request, 'auth/login.html')

            login(request, user)

            # Reset failed attempts
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login_ip = get_client_ip(request)
            user.save(update_fields=['failed_login_attempts', 'locked_until', 'last_login_ip'])

            # Session expiry
            if not remember_me:
                request.session.set_expiry(0)  # Browser session
            else:
                request.session.set_expiry(timedelta(days=7))  # 7 days

            # Log login
            try:
                LoginHistory.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    is_successful=True
                )
            except Exception as e:
                pass  # Continue even if login history logging fails

            # Redirect
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
        else:
            # Increment failed attempts
            from apps.authentication.models import User as UserModel
            try:
                failed_user = UserModel.objects.get(email=email)
                failed_user.failed_login_attempts += 1
                if failed_user.failed_login_attempts >= 5:
                    failed_user.locked_until = timezone.now() + timedelta(minutes=30)
                    messages.error(request, 'Too many failed attempts. Account locked for 30 minutes.')
                else:
                    messages.error(request, f'Invalid email or password. {5 - failed_user.failed_login_attempts} attempts remaining.')
                failed_user.save(update_fields=['failed_login_attempts', 'locked_until'])
                # Log failed login attempt
                try:
                    LoginHistory.objects.create(
                        user=failed_user,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                        is_successful=False
                    )
                except Exception:
                    pass  # Continue even if logging fails
            except UserModel.DoesNotExist:
                messages.error(request, 'Invalid email or password.')

    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    # Update logout time
    LoginHistory.objects.filter(
        user=request.user, logout_time__isnull=True
    ).update(logout_time=timezone.now())

    logout(request)
    messages.success(request, 'You have been signed out successfully.')
    return redirect('authentication:login')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        current = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
        elif new_pass != confirm:
            messages.error(request, 'Passwords do not match.')
        elif len(new_pass) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            request.user.set_password(new_pass)
            request.user.password_changed_at = timezone.now()
            request.user.must_change_password = False
            request.user.save()
            messages.success(request, 'Password changed successfully. Please sign in again.')
            logout(request)
            return redirect('authentication:login')

    return render(request, 'auth/change_password.html')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        from apps.authentication.models import User
        try:
            user = User.objects.get(email=email)
            # Send password reset email (task)
            from apps.notifications.tasks import send_password_reset_email
            send_password_reset_email.delay(str(user.id))
            messages.success(request, 'Password reset link sent to your email.')
        except User.DoesNotExist:
            messages.success(request, 'If this email exists, a reset link has been sent.')
        return redirect('authentication:login')

    return render(request, 'auth/forgot_password.html')


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
