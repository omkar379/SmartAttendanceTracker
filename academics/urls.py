
from django.urls import path
from . import views

urlpatterns = [
    path(
        'daily-timetable/',
        views.daily_timetable,
        name='daily_timetable'
    ),
]
