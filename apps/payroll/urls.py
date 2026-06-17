"""WorkSphere HR - Payroll Web URLs"""
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from apps.authentication.utils import employee_portal_only, payroll_portal_only

app_name = 'payroll'

def payroll_dashboard(request):
    return render(request, 'payroll/modern_payroll.html')

def my_payslips_view(request):
    today = timezone.now()
    years = list(range(today.year - 3, today.year + 1))
    return render(request, 'payroll/my_payslips.html', {'years': years, 'current_year': today.year})

urlpatterns = [
    path('', payroll_portal_only(payroll_dashboard), name='index'),
    path('process/', payroll_portal_only(payroll_dashboard), name='process'),
    path('payslips/', payroll_portal_only(payroll_dashboard), name='payslips'),
    path('my-payslips/', employee_portal_only(my_payslips_view), name='my_payslips'),
]
