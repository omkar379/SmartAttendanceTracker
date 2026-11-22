
from django.urls import path
from . import views

urlpatterns = [
    path('mark/', views.mark_attendance, name='mark_attendance'),

    path('view/', views.view_attendance, name='view_attendance'),

    path('generate-qr/', views.generate_qr, name='generate_qr'),

    path(
    'scan/<uuid:token>/',
    views.scan_attendance,
    name='scan_attendance'
),
]
