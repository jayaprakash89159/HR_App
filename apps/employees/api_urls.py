"""WorkSphere HR - Employee API URLs"""
from django.urls import path
from .views import (
    EmployeeListAPIView, EmployeeDetailAPIView,
    DepartmentListAPIView, DesignationListAPIView, MyProfileAPIView
)

urlpatterns = [
    path('',               EmployeeListAPIView.as_view(),    name='employee_list'),
    path('me/',            MyProfileAPIView.as_view(),       name='my_profile'),
    path('<uuid:pk>/',     EmployeeDetailAPIView.as_view(),  name='employee_detail'),
    path('departments/',   DepartmentListAPIView.as_view(),  name='department_list'),
    path('designations/',  DesignationListAPIView.as_view(), name='designation_list'),
]
