"""WorkSphere HR - Leave Web URLs"""
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
app_name = 'leave'
urlpatterns = [
    path('', login_required(lambda r: render(r, 'leave/modern_leave.html')), name='my_leaves'),
    path('apply/', login_required(lambda r: render(r, 'leave/modern_leave.html')), name='apply'),
    path('my-leaves/', login_required(lambda r: render(r, 'leave/modern_leave.html')), name='my_leaves_list'),
    path('balance/', login_required(lambda r: render(r, 'leave/modern_leave.html')), name='balance'),
    path('holidays/', login_required(lambda r: render(r, 'leave/modern_leave.html')), name='holidays'),
    path('approvals/', login_required(lambda r: render(r, 'leave/modern_leave.html')), name='approvals'),
    path('requests/', login_required(lambda r: render(r, 'leave/modern_leave.html')), name='requests'),
]
