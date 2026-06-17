"""WorkSphere HR - Payroll API URLs"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('payslips/', api_views.MyPayslipsAPIView.as_view(), name='my_payslips'),
    path('payslips/<uuid:pk>/', api_views.PayslipDetailAPIView.as_view(), name='payslip_detail'),
    path('summary/', api_views.PayrollSummaryAPIView.as_view(), name='payroll_summary'),
]
