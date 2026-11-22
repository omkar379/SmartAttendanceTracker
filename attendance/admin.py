
from django.contrib import admin
from .models import Attendance, AttendanceSession, AttendanceHistory


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'classroom',
        'subject',
        'date',
        'status',
    )

    list_filter = (
        'status',
        'date',
        'classroom',
        'subject',
    )

    search_fields = (
        'student__username',
        'subject__name',
        'classroom__name',
    )


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = (
        'teacher',
        'classroom',
        'subject',
        'date',
        'is_active',
    )

    list_filter = (
        'date',
        'is_active',
        'subject',
    )


@admin.register(AttendanceHistory)
class AttendanceHistoryAdmin(admin.ModelAdmin):

    list_display = (
        'attendance',
        'old_status',
        'new_status',
        'changed_by',
        'changed_at',
    )

    list_filter = (
        'old_status',
        'new_status',
        'changed_at',
    )

    search_fields = (
        'attendance__student__username',
        'changed_by__username',
    )

    readonly_fields = (
        'attendance',
        'old_status',
        'new_status',
        'changed_by',
        'changed_at',
    )
