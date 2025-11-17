"""
Accounts App URLs Configuration
Reference: https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('change-password/', views.change_password, name='change_password'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
]
