"""
Dashboard App URLs Configuration
Reference: https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/<slug:slug>/', views.blog_analytics, name='blog_analytics'),
]
