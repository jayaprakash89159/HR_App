"""WorkSphere HR - Shifts Web URLs"""
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
app_name = 'shifts'
urlpatterns = [
    path('', login_required(lambda r: render(r, 'shifts/list.html')), name='list'),
]
