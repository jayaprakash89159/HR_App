"""WorkSphere HR - Shifts Web URLs"""
from django.urls import path
from django.shortcuts import render
from apps.authentication.utils import hr_portal_only
app_name = 'shifts'
urlpatterns = [
    path('', hr_portal_only(lambda r: render(r, 'shifts/list.html')), name='list'),
]
