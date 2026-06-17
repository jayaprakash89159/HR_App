"""WorkSphere HR - Leave Management API URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('types/', views.LeaveTypesAPIView.as_view(), name='leave_types'),
    path('balances/', views.LeaveBalancesAPIView.as_view(), name='leave_balances'),
    path('applications/', views.LeaveApplicationsAPIView.as_view(), name='leave_applications'),
    path('applications/<uuid:pk>/', views.LeaveApplicationDetailAPIView.as_view(), name='leave_application_detail'),
    path('holidays/', views.HolidaysAPIView.as_view(), name='holidays'),
    path('pending-approvals/', views.LeavePendingApprovalsAPIView.as_view(), name='pending_approvals'),
]
