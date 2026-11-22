
"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from accounts import views

urlpatterns = [

    # Custom Admin Dashboard
    path(
        'dashboard/admin/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    # Student Management
    path(
        'dashboard/students/',
        views.admin_students,
        name='admin_students'
    ),

    # Teacher Management
    path(
        'dashboard/teachers/',
        views.admin_teachers,
        name='admin_teachers'
    ),

    # Django Admin
    path('admin/', admin.site.urls),

    # Other Apps
    path('', include('accounts.urls')),
    path('attendance/', include('attendance.urls')),
    path('reports/', include('reports.urls')),
    path('academics/', include('academics.urls')),
]
