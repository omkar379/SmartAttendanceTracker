
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.CharField(max_length=50)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Timetable(models.Model):

    DAY_CHOICES = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
    ]

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    day = models.CharField(
        max_length=10,
        choices=DAY_CHOICES
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    def clean(self):

        super().clean()

        if self.start_time and self.end_time:

            if self.start_time >= self.end_time:
                raise ValidationError(
                    "End time must be after start time."
                )

        if not all([
            self.classroom_id,
            self.teacher_id,
            self.day,
            self.start_time,
            self.end_time
        ]):
            return

        overlapping = Timetable.objects.filter(
            day=self.day,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        classroom_conflict = overlapping.filter(
            classroom=self.classroom
        ).exists()

        teacher_conflict = overlapping.filter(
            teacher=self.teacher
        ).exists()

        if classroom_conflict:
            raise ValidationError(
                "This classroom already has a class at this time."
            )

        if teacher_conflict:
            raise ValidationError(
                "This teacher already has a class at this time."
            )

    def __str__(self):
        return (
            f"{self.day} - {self.subject.name} "
            f"({self.start_time} - {self.end_time})"
        )
