
import uuid

from django.db import models
from django.contrib.auth.models import User
from academics.models import Subject, ClassRoom


class Attendance(models.Model):

    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    qr_session = models.ForeignKey(
    'AttendanceSession',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='attendance_records'
)

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.date}"


class AttendanceSession(models.Model):

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.name} - {self.date}"

class AttendanceHistory(models.Model):

    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name='history'
    )

    old_status = models.CharField(
        max_length=10,
        choices=Attendance.STATUS_CHOICES
    )

    new_status = models.CharField(
        max_length=10,
        choices=Attendance.STATUS_CHOICES
    )

    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    changed_at = models.DateTimeField(auto_now_add=True)

    remarks = models.TextField(blank=True)

    def __str__(self):
        return (
            f"{self.attendance.student.username} - "
            f"{self.old_status} to {self.new_status}"
        )
