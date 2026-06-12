"""WorkSphere HR - Employee Web URLs"""
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
app_name = 'employees'
urlpatterns = [
    path('', login_required(lambda r: render(r, 'employees/modern_list.html')), name='list'),
    path('profile/', login_required(lambda r: render(r, 'employees/profile.html')), name='profile'),
    path('documents/', login_required(lambda r: render(r, 'employees/documents.html')), name='documents'),
]
