from django import forms
from django.contrib.auth.models import User

from .models import Timetable
from accounts.models import UserProfile


class TimetableForm(forms.ModelForm):

    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(
            userprofile__role='TEACHER'
        ),
        label="Teacher"
    )

    class Meta:
        model = Timetable
        fields = '__all__'