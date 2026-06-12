"""WorkSphere HR - Dashboard Web URLs"""
from django.urls import path
from . import views
app_name = 'dashboard'
urlpatterns = [path('', views.home, name='home')]
