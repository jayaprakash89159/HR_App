"""WorkSphere HR - Reports Web URLs"""
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
app_name = 'reports'
urlpatterns = [
    path('', login_required(lambda r: render(r, 'reports/modern_reports.html')), name='index'),
    path('attendance/', login_required(lambda r: render(r, 'reports/modern_reports.html')), name='attendance'),
    path('analytics/', login_required(lambda r: render(r, 'reports/modern_reports.html')), name='analytics'),
]
