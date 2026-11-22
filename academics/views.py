
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone

from accounts.models import UserProfile
from .models import Timetable


@login_required
def daily_timetable(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    today = timezone.localdate()
    current_time = timezone.localtime().time()

    day_name = today.strftime('%A').upper()

    timetable = Timetable.objects.filter(
        day=day_name
    ).select_related(
        'classroom',
        'subject',
        'teacher'
    )

    # Student: Show only assigned classroom lectures
    if profile.role == 'STUDENT':

        if not profile.classroom:
            timetable = timetable.none()
        else:
            timetable = timetable.filter(
                classroom=profile.classroom
            )

    # Teacher: Show only assigned lectures
    elif profile.role == 'TEACHER':

        timetable = timetable.filter(
            teacher=request.user
        )

    else:
        return HttpResponseForbidden("Access denied")

    timetable = timetable.order_by('start_time')

    upcoming_lecture = None

    for lecture in timetable:

        if current_time >= lecture.end_time:
            lecture.status = 'COMPLETED'

        elif lecture.start_time <= current_time < lecture.end_time:
            lecture.status = 'CURRENT'

        else:
            lecture.status = 'UPCOMING'

            if upcoming_lecture is None:
                upcoming_lecture = lecture

    return render(
        request,
        'academics/daily_timetable.html',
        {
            'timetable': timetable,
            'today': today,
            'day_name': day_name,
            'current_time': current_time,
            'upcoming_lecture': upcoming_lecture,
        }
    )
