from django.urls import path
from . import views

urlpatterns = [
    path(
        'attendance/',
        views.attendance_report,
        name='attendance_report'
    ),

    path(
        'send-attendance-alert/',
        views.send_attendance_alert,
        name='send_attendance_alert'
    ),
]