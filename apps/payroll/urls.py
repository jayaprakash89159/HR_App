"""WorkSphere HR - Payroll Web URLs"""
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
app_name = 'payroll'
urlpatterns = [
    path('', login_required(lambda r: render(r, 'payroll/modern_payroll.html')), name='index'),
    path('process/', login_required(lambda r: render(r, 'payroll/modern_payroll.html')), name='process'),
    path('payslips/', login_required(lambda r: render(r, 'payroll/modern_payroll.html')), name='payslips'),
    path('my-payslips/', login_required(lambda r: render(r, 'payroll/modern_payroll.html')), name='my_payslips'),
]
