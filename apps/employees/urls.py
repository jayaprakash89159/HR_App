"""WorkSphere HR - Employee Web URLs"""
from django.urls import path
from django.shortcuts import render
from apps.authentication.utils import hr_portal_only
app_name = 'employees'
urlpatterns = [
    path('', hr_portal_only(lambda r: render(r, 'employees/modern_list.html')), name='list'),
    path('profile/', hr_portal_only(lambda r: render(r, 'employees/profile.html')), name='profile'),
    path('documents/', hr_portal_only(lambda r: render(r, 'employees/documents.html')), name='documents'),
]
