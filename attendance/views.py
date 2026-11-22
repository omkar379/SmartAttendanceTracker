
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import UserProfile
from academics.models import ClassRoom, Subject
from .models import Attendance, AttendanceSession, AttendanceHistory

import qrcode
import base64
from io import BytesIO


# Mark Attendance Manually
@login_required
def mark_attendance(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'TEACHER':
        return HttpResponseForbidden("Access denied")

    if request.method == 'POST':

        student_id = request.POST.get('student')
        classroom_id = request.POST.get('classroom')
        subject_id = request.POST.get('subject')
        date = request.POST.get('date')
        status = request.POST.get('status')

        attendance = Attendance.objects.filter(
            student_id=student_id,
            classroom_id=classroom_id,
            subject_id=subject_id,
            date=date
        ).order_by('id').first()

        if attendance:

            old_status = attendance.status

            if old_status != status:

                AttendanceHistory.objects.create(
                    attendance=attendance,
                    old_status=old_status,
                    new_status=status,
                    changed_by=request.user,
                    remarks='Attendance updated by teacher'
                )

                attendance.status = status
                attendance.save(update_fields=['status'])

        else:

            Attendance.objects.create(
                student_id=student_id,
                classroom_id=classroom_id,
                subject_id=subject_id,
                date=date,
                status=status
            )

        return redirect('attendance_report')

    context = {
        'students': User.objects.filter(
            userprofile__role='STUDENT'
        ),
        'classrooms': ClassRoom.objects.all(),
        'subjects': Subject.objects.all(),
    }

    return render(
        request,
        'attendance/mark_attendance.html',
        context
    )


# View Attendance
@login_required
def view_attendance(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'TEACHER':
        return HttpResponseForbidden("Access denied")

    records = Attendance.objects.select_related(
        'student',
        'classroom',
        'subject'
    ).order_by('-date')

    context = {
        'records': records,
    }

    return render(
        request,
        'attendance/view_attendance.html',
        context
    )


# Generate QR Code
@login_required
def generate_qr(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'TEACHER':
        return HttpResponseForbidden("Access denied")

    if request.method == 'POST':

        classroom_id = request.POST.get('classroom')
        subject_id = request.POST.get('subject')

        session = AttendanceSession.objects.create(
            teacher=request.user,
            classroom_id=classroom_id,
            subject_id=subject_id,
            date=timezone.localdate()
        )

        qr_url = (
            f"{request.scheme}://{request.get_host()}"
            f"/attendance/scan/{session.token}/"
        )

        qr = qrcode.make(qr_url)

        buffer = BytesIO()
        qr.save(buffer, format='PNG')

        qr_image = base64.b64encode(
            buffer.getvalue()
        ).decode('utf-8')

        context = {
            'qr_image': qr_image,
            'session': session,
        }

        return render(
            request,
            'attendance/generate_qr.html',
            context
        )

    context = {
        'classrooms': ClassRoom.objects.all(),
        'subjects': Subject.objects.all(),
    }

    return render(
        request,
        'attendance/generate_qr.html',
        context
    )


# Scan QR Code and Mark Attendance
@login_required
def scan_attendance(request, token):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'STUDENT':
        return HttpResponseForbidden(
            "Only students can mark QR attendance"
        )

    session = get_object_or_404(
        AttendanceSession,
        token=token,
        is_active=True
    )

    if session.date != timezone.localdate():
        return HttpResponseForbidden(
            "This QR Code has expired"
        )

    if request.method == 'POST':

        existing_record = Attendance.objects.filter(
            student=request.user,
            qr_session=session
        ).first()

        if existing_record:

            context = {
                'session': session,
                'already_marked': True,
            }

        else:

            Attendance.objects.create(
                student=request.user,
                classroom=session.classroom,
                subject=session.subject,
                date=session.date,
                status='PRESENT',
                qr_session=session
            )

            context = {
                'session': session,
                'success': True,
            }

        return render(
            request,
            'attendance/scan_qr.html',
            context
        )

    return render(
        request,
        'attendance/scan_qr.html',
        {'session': session}
    )
