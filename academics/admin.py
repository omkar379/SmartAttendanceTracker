from django.contrib import admin
from .models import Department, ClassRoom, Subject, Timetable
from .forms import TimetableForm


admin.site.register(Department)
admin.site.register(ClassRoom)
admin.site.register(Subject)


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    form = TimetableForm