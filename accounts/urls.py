
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Login and Logout
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Admin Dashboard
    path(
        'admin/dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    # Student Management
    path(
        'management/students/',
        views.admin_students,
        name='admin_students'
    ),

    # Add Student
    path(
        'management/students/add/',
        views.add_student,
        name='add_student'
    ),

    # Edit Student
    path(
        'management/students/edit/<int:student_id>/',
        views.edit_student,
        name='edit_student'
    ),

    # Teacher Management
    path(
        'management/teachers/',
        views.admin_teachers,
        name='admin_teachers'
    ),

    # Teacher Dashboard
    path(
        'teacher/dashboard/',
        views.teacher_dashboard,
        name='teacher_dashboard'
    ),

    path(
        'teacher/timetable/',
        views.teacher_timetable,
        name='teacher_timetable'
    ),

    # Student Dashboard
    path(
        'student/dashboard/',
        views.student_dashboard,
        name='student_dashboard'
    ),

    path(
        'student/timetable/',
        views.student_timetable,
        name='student_timetable'
    ),

    # Delete Student
path(
    'management/students/delete/<int:student_id>/',
    views.delete_student,
    name='delete_student'
),

# Add Teacher
path(
    'management/teachers/add/',
    views.add_teacher,
    name='add_teacher'
),
# Edit Teacher
path(
    'management/teachers/edit/<int:teacher_id>/',
    views.edit_teacher,
    name='edit_teacher'
),
# Delete Teacher
path(
    'management/teachers/delete/<int:teacher_id>/',
    views.delete_teacher,
    name='delete_teacher'
),
# Add Department
path(
    'management/departments/add/',
    views.add_department,
    name='add_department'
),
# Department List
path(
    'management/departments/',
    views.admin_departments,
    name='admin_departments'
),
# Edit Department
path(
    'management/departments/edit/<int:department_id>/',
    views.edit_department,
    name='edit_department'
),
# Delete Department
path(
    'management/departments/delete/<int:department_id>/',
    views.delete_department,
    name='delete_department'
),
# Subject List
path(
    'management/subjects/',
    views.admin_subjects,
    name='admin_subjects'
),

# Add Subject
path(
    'management/subjects/add/',
    views.add_subject,
    name='add_subject'
),
# Edit Subject
path(
    'management/subjects/edit/<int:subject_id>/',
    views.edit_subject,
    name='edit_subject'
),

# Delete Subject
path(
    'management/subjects/delete/<int:subject_id>/',
    views.delete_subject,
    name='delete_subject'
),

]
