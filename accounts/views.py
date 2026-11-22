
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from academics.models import ClassRoom
from .models import UserProfile
from attendance.models import Attendance
from academics.models import Timetable, Department, Subject
from django.shortcuts import get_object_or_404
from academics.models import ClassRoom

# Home Page
def home(request):
    return render(request, 'home.html')


# User Login
def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            try:
                profile = user.userprofile
            except UserProfile.DoesNotExist:
                return HttpResponseForbidden("Profile not found")

            login(request, user)

            if profile.role == 'TEACHER':
                return redirect('teacher_dashboard')

            elif profile.role == 'STUDENT':
                return redirect('student_dashboard')

            elif profile.role == 'ADMIN':
                return redirect('admin_dashboard')

            else:
                return HttpResponseForbidden("Access denied")

        else:
            return render(
                request,
                'login.html',
                {'error': 'Invalid username or password'}
            )

    return render(request, 'login.html')


# Admin Dashboard
@login_required
def admin_dashboard(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    total_students = UserProfile.objects.filter(
        role='STUDENT'
    ).count()

    total_teachers = UserProfile.objects.filter(
        role='TEACHER'
    ).count()

    total_departments = Department.objects.count()
    total_subjects = Subject.objects.count()
    total_attendance = Attendance.objects.count()

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_departments': total_departments,
        'total_subjects': total_subjects,
        'total_attendance': total_attendance,
    }

    return render(
        request,
        'admin_dashboard.html',
        context
    )


# Teacher Dashboard
@login_required
def teacher_dashboard(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'TEACHER':
        return HttpResponseForbidden("Access denied")

    return render(request, 'teacher_dashboard.html')


# Student Dashboard
@login_required
def student_dashboard(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'STUDENT':
        return HttpResponseForbidden("Access denied")

    records = Attendance.objects.filter(
        student=request.user
    )

    total_classes = records.count()
    present_classes = records.filter(status='PRESENT').count()
    absent_classes = records.filter(status='ABSENT').count()

    if total_classes > 0:
        percentage = (present_classes / total_classes) * 100
    else:
        percentage = 0

    low_attendance = percentage < 75

    if low_attendance:
        required_classes = max(
            0,
            int(
                (0.75 * total_classes - present_classes) / 0.25
            ) + (
                1 if (0.75 * total_classes - present_classes)
                % 0.25 != 0 else 0
            )
        )

        prediction_message = (
            f"Attend the next {required_classes} "
            "consecutive classes to reach 75% attendance."
        )

    else:
        required_classes = 0
        prediction_message = (
            "Your attendance target of 75% is achieved!"
        )

    context = {
        'records': records.order_by('-date'),
        'total_classes': total_classes,
        'present_classes': present_classes,
        'absent_classes': absent_classes,
        'percentage': round(percentage, 2),
        'low_attendance': low_attendance,
        'required_classes': required_classes,
        'prediction_message': prediction_message,
    }

    return render(
        request,
        'student_dashboard.html',
        context
    )


# Student Timetable
@login_required
def student_timetable(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'STUDENT':
        return HttpResponseForbidden("Access denied")

    if not profile.classroom:
        return render(
            request,
            'student_timetable.html',
            {
                'timetable': [],
                'error': 'No classroom assigned.'
            }
        )

    timetable = Timetable.objects.filter(
        classroom=profile.classroom
    ).select_related(
        'subject',
        'classroom',
        'teacher'
    ).order_by(
        'day',
        'start_time'
    )

    return render(
        request,
        'student_timetable.html',
        {'timetable': timetable}
    )


# Teacher Timetable
@login_required
def teacher_timetable(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'TEACHER':
        return HttpResponseForbidden("Access denied")

    timetable = Timetable.objects.filter(
        teacher=request.user
    ).select_related(
        'subject',
        'classroom',
        'teacher'
    ).order_by(
        'day',
        'start_time'
    )

    return render(
        request,
        'teacher_timetable.html',
        {'timetable': timetable}
    )


# User Logout
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


# Admin - Student Management
@login_required
def admin_students(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    students = UserProfile.objects.filter(
        role='STUDENT'
    ).select_related('user', 'classroom')

    return render(
        request,
        'admin_students.html',
        {'students': students}
    )


# Admin - Teacher Management
@login_required
def admin_teachers(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    teachers = UserProfile.objects.filter(
        role='TEACHER'
    ).select_related('user')

    return render(
        request,
        'admin_teachers.html',
        {'teachers': teachers}
    )


# Admin - Add Student
@login_required
def add_student(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    classrooms = ClassRoom.objects.all()

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        classroom_id = request.POST.get('classroom')

        if not username or not password:
            return render(request, 'add_student.html', {
                'classrooms': classrooms,
                'error': 'Username and password are required.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'add_student.html', {
                'classrooms': classrooms,
                'error': 'Username already exists.'
            })

        classroom = None

        if classroom_id:
            try:
                classroom = ClassRoom.objects.get(id=classroom_id)
            except ClassRoom.DoesNotExist:
                return render(request, 'add_student.html', {
                    'classrooms': classrooms,
                    'error': 'Invalid classroom selected.'
                })

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        UserProfile.objects.create(
            user=user,
            role='STUDENT',
            classroom=classroom
        )

        return redirect('admin_students')

    return render(
        request,
        'add_student.html',
        {'classrooms': classrooms}
    )
# Admin - Edit Student
@login_required
def edit_student(request, student_id):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    student = get_object_or_404(
        UserProfile,
        id=student_id,
        role='STUDENT'
    )

    if request.method == 'POST':

        student.user.first_name = request.POST.get('first_name', '').strip()
        student.user.last_name = request.POST.get('last_name', '').strip()
        student.user.email = request.POST.get('email', '').strip()

        classroom_id = request.POST.get('classroom')

        if classroom_id:
            student.classroom = get_object_or_404(
                ClassRoom,
                id=classroom_id
            )
        else:
            student.classroom = None

        student.user.save()
        student.save()

        return redirect('admin_students')

    classrooms = ClassRoom.objects.all()

    return render(request, 'edit_student.html', {
        'student': student,
        'classrooms': classrooms
    })

# Admin - Delete Student
@login_required
def delete_student(request, student_id):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    if request.method != 'POST':
        return HttpResponseForbidden("Invalid request")

    student = get_object_or_404(
        UserProfile,
        id=student_id,
        role='STUDENT'
    )

    student.user.delete()

    return redirect('admin_students')

# Admin - Add Teacher
@login_required
def add_teacher(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not username or not password:
            return render(request, 'add_teacher.html', {
                'error': 'Username and password are required.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'add_teacher.html', {
                'error': 'Username already exists.'
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        UserProfile.objects.create(
            user=user,
            role='TEACHER',
            phone=phone
        )

        return redirect('admin_teachers')

    return render(request, 'add_teacher.html')

 
# Admin - Edit Teacher
@login_required
def edit_teacher(request, teacher_id):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    teacher = get_object_or_404(
        UserProfile,
        id=teacher_id,
        role='TEACHER'
    )

    if request.method == 'POST':

        teacher.user.first_name = request.POST.get(
            'first_name', ''
        ).strip()

        teacher.user.last_name = request.POST.get(
            'last_name', ''
        ).strip()

        teacher.user.email = request.POST.get(
            'email', ''
        ).strip()

        teacher.phone = request.POST.get(
            'phone', ''
        ).strip()

        teacher.user.save()
        teacher.save()

        return redirect('admin_teachers')

    return render(request, 'edit_teacher.html', {
        'teacher': teacher
    })

# Admin - Delete Teacher
@login_required
def delete_teacher(request, teacher_id):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    if request.method != 'POST':
        return HttpResponseForbidden("Invalid request")

    teacher = get_object_or_404(
        UserProfile,
        id=teacher_id,
        role='TEACHER'
    )

    teacher.user.delete()

    return redirect('admin_teachers')

# Admin - Add Department
@login_required
def add_department(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()

        if not name or not code:
            return render(request, 'add_department.html', {
                'error': 'Department name and code are required.'
            })

        if Department.objects.filter(code=code).exists():
            return render(request, 'add_department.html', {
                'error': 'Department code already exists.'
            })

        Department.objects.create(
            name=name,
            code=code
        )

        return redirect('admin_departments')

    return render(request, 'add_department.html')
# Admin - Department List
@login_required
def admin_departments(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    departments = Department.objects.all().order_by('name')

    return render(request, 'admin_departments.html', {
        'departments': departments
    })
# Admin - Edit Department
@login_required
def edit_department(request, department_id):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    department = get_object_or_404(Department, id=department_id)

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()

        if not name or not code:
            return render(request, 'edit_department.html', {
                'department': department,
                'error': 'Department name and code are required.'
            })

        if Department.objects.filter(code=code).exclude(id=department_id).exists():
            return render(request, 'edit_department.html', {
                'department': department,
                'error': 'Department code already exists.'
            })

        department.name = name
        department.code = code
        department.save()

        return redirect('admin_departments')

    return render(request, 'edit_department.html', {
        'department': department
    })
# Admin - Delete Department
@login_required
def delete_department(request, department_id):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    if request.method != 'POST':
        return HttpResponseForbidden("Invalid request")

    department = get_object_or_404(Department, id=department_id)

    department.delete()

    return redirect('admin_departments')
 
# Admin - Subject List
@login_required
def admin_subjects(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    subjects = Subject.objects.select_related(
        'classroom',
        'classroom__department'
    ).all().order_by('name')

    return render(request, 'admin_subjects.html', {
        'subjects': subjects
    })


# Admin - Add Subject
@login_required
def add_subject(request):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    classrooms = ClassRoom.objects.all().order_by('name')

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        classroom_id = request.POST.get('classroom')

        if not name or not code or not classroom_id:
            return render(request, 'add_subject.html', {
                'classrooms': classrooms,
                'error': 'All fields are required.'
            })

        if Subject.objects.filter(code=code).exists():
            return render(request, 'add_subject.html', {
                'classrooms': classrooms,
                'error': 'Subject code already exists.'
            })

        classroom = get_object_or_404(
            ClassRoom,
            id=classroom_id
        )

        Subject.objects.create(
            name=name,
            code=code,
            classroom=classroom
        )

        return redirect('admin_subjects')

    return render(request, 'add_subject.html', {
        'classrooms': classrooms
    })
 
# Admin - Edit Subject
@login_required
def edit_subject(request, subject_id):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    subject = get_object_or_404(Subject, id=subject_id)
    classrooms = ClassRoom.objects.all().order_by('name')

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        classroom_id = request.POST.get('classroom')

        if not name or not code or not classroom_id:
            return render(request, 'edit_subject.html', {
                'subject': subject,
                'classrooms': classrooms,
                'error': 'All fields are required.'
            })

        if Subject.objects.filter(code=code).exclude(id=subject_id).exists():
            return render(request, 'edit_subject.html', {
                'subject': subject,
                'classrooms': classrooms,
                'error': 'Subject code already exists.'
            })

        classroom = get_object_or_404(
            ClassRoom,
            id=classroom_id
        )

        subject.name = name
        subject.code = code
        subject.classroom = classroom
        subject.save()

        return redirect('admin_subjects')

    return render(request, 'edit_subject.html', {
        'subject': subject,
        'classrooms': classrooms
    })
  
# Admin - Delete Subject
@login_required
def delete_subject(request, subject_id):

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found")

    if profile.role != 'ADMIN':
        return HttpResponseForbidden("Access denied")

    if request.method != 'POST':
        return HttpResponseForbidden("Invalid request")

    subject = get_object_or_404(Subject, id=subject_id)

    # Prevent deletion if subject is used in timetable
    if Timetable.objects.filter(subject=subject).exists():
        return redirect('admin_subjects')

    subject.delete()

    return redirect('admin_subjects')

