
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Count, Q

from django.core.mail import send_mail

from attendance.models import Attendance
from accounts.models import UserProfile


@login_required
def attendance_report(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    # Student-wise attendance
    if profile.role == 'STUDENT':
        records = Attendance.objects.filter(
            student=request.user
        )

    # Teacher can view all attendance records
    elif profile.role == 'TEACHER':
        records = Attendance.objects.all()

    else:
        return HttpResponseForbidden("Access denied")

    total_classes = records.count()

    present_classes = records.filter(
        status='PRESENT'
    ).count()

    absent_classes = records.filter(
        status='ABSENT'
    ).count()

    if total_classes > 0:
        percentage = (
            present_classes / total_classes
        ) * 100
    else:
        percentage = 0

    low_attendance = percentage < 75

    if low_attendance:
        required_classes = max(
            0,
            int(
                (0.75 * total_classes - present_classes)
                / 0.25
            ) + (
                1 if (0.75 * total_classes - present_classes)
                % 0.25 != 0 else 0
            )
        )
    else:
        required_classes = 0

    # Subject-wise Analytics
    subject_analytics = records.values(
        'subject__name'
    ).annotate(
        total=Count('id'),
        present=Count(
            'id',
            filter=Q(status='PRESENT')
        ),
        absent=Count(
            'id',
            filter=Q(status='ABSENT')
        )
    ).order_by('subject__name')

    for subject in subject_analytics:
        if subject['total'] > 0:
            subject['percentage'] = round(
                subject['present']
                / subject['total'] * 100,
                2
            )
        else:
            subject['percentage'] = 0

    context = {
        'records': records.order_by('-date'),
        'total_classes': total_classes,
        'present_classes': present_classes,
        'absent_classes': absent_classes,
        'percentage': round(percentage, 2),
        'low_attendance': low_attendance,
        'required_classes': required_classes,
        'subject_analytics': subject_analytics,
    }

    return render(
        request,
        'reports/attendance_report.html',
        context
    )

# Send Low Attendance Email Alert
@login_required
@require_POST
def send_attendance_alert(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'TEACHER':
        return HttpResponseForbidden("Access denied")

    students = UserProfile.objects.filter(
        role='STUDENT'
    ).select_related('user')

    sent_count = 0

    for student_profile in students:

        student = student_profile.user

        records = Attendance.objects.filter(
            student=student
        )

        total_classes = records.count()

        if total_classes == 0:
            continue

        present_classes = records.filter(
            status='PRESENT'
        ).count()

        percentage = (
            present_classes / total_classes
        ) * 100

        if percentage < 75 and student.email:

            send_mail(
                subject='Low Attendance Alert',
                message=(
                    f'Hello {student.username},\n\n'
                    f'Your current attendance is '
                    f'{percentage:.2f}%.\n'
                    'Your attendance is below 75%.\n'
                    'Please attend upcoming classes regularly.'
                ),
                from_email=None,
               recipient_list=[
    student.email
],
                fail_silently=False,
            )

            sent_count += 1

    return render(
        request,
        'reports/attendance_alert_result.html',
        {'sent_count': sent_count}
    )
