 
 
from django.core.mail import EmailMultiAlternatives  
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages # For displaying feedback messages

 
 
from django.db.models import Prefetch, Count, Q
from django.http import JsonResponse
import base64
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


from .models import User, Student, Lecturer, Course, Enrollment, ClassSession, Attendance
from .forms import (
    CustomUserCreationForm, StudentForm, LecturerForm, CourseForm,
    EnrollmentForm, ClassSessionForm, AttendanceForm
)
 
from .forms import AnnouncementForm  
 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch, Count, Q
from django.http import JsonResponse
import base64
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import timedelta
from datetime import datetime, time
from django.utils import timezone
from .models import User, Student, Lecturer, Course, Enrollment, ClassSession, Attendance
from .forms import (
    CustomUserCreationForm, StudentForm, LecturerForm, CourseForm,
    EnrollmentForm, ClassSessionForm, AttendanceForm
)

import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

# --- Helper functions for user type checks ---
def is_student(user):
    return user.is_authenticated and hasattr(user, 'student_profile') and user.user_type == 'Student'

def is_lecturer(user):
    return user.is_authenticated and hasattr(user, 'lecturer_profile') and user.user_type == 'Lecturer'

def is_admin(user):
    return user.is_authenticated and user.is_staff and user.user_type == 'Admin'


# --- Basic Authentication Views ---
 


 
def is_student(user):
    return user.is_authenticated and hasattr(user, 'student_profile') and user.user_type == 'Student'

def is_lecturer(user):
    return user.is_authenticated and hasattr(user, 'lecturer_profile') and user.user_type == 'Lecturer'

def is_admin(user):
    return user.is_authenticated and user.is_staff and user.user_type == 'Admin'


# --- Basic Authentication Views ---

def custom_login_view(request):
    """
    Handles user login. Authenticates based on username (student/staff number) and password.
    Redirects to the appropriate dashboard based on user_type.
    The role selection from the form has been removed for a cleaner UI.
    """
    if request.method == 'POST':
        user_number = request.POST.get('user_number')
        password = request.POST.get('password')
        

        user = authenticate(request, username=user_number, password=password)

        if user is not None:
 

            login(request, user) # Log the user in

            # Redirect based on user_type fetched directly from the authenticated user
            if user.user_type == 'Student':
                messages.success(request, f"Welcome, {user.first_name}! You're logged in as a Student.")
                return redirect('student_dashboard')  
            elif user.user_type == 'Lecturer':
                messages.success(request, f"Welcome, {user.first_name}! You're logged in as a Lecturer.")
                return redirect('lecturer_dashboard')  
            elif user.user_type == 'Admin':
                 return redirect('admin:index') # Redirect to Django admin site
            else:
                 return redirect('home') # Fallback for other user types

        else:
            # Authentication failed
            messages.error(request, "You could not be authenticated, please check your username/password then try again")
             
            return render(request, 'login.html') 
    else:
        # For GET requests, just render the empty login form
        return render(request, 'login.html')

def custom_logout_view(request):
    """
    Logs out the user and redirects to the login page with a success message.
    """
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('login')
 

# --- Home View ---
def home(request):
    """
    Renders the home page.
    """
     
    return render(request, 'home.html')


# --- Dashboard Views ---

@login_required
 
@user_passes_test(is_student, login_url='/webapp/login/')
def student_dashboard(request):
    """
    Displays the dashboard for a logged-in student.
    Fetches student-specific details, enrollments, attendance, and upcoming sessions.
    """
    student_profile = request.user.student_profile
    user_data = request.user

    enrolled_courses_qs = Enrollment.objects.filter(student=student_profile).select_related('course__lecturer__user')

    subjects_data = []
    for enrollment in enrolled_courses_qs:
        subjects_data.append({
            'id': enrollment.course.course_code,
            'course_code': enrollment.course.course_code,
            'course_name': enrollment.course.course_name,
            'lecturer_name': enrollment.course.lecturer.user.get_full_name() if enrollment.course.lecturer else 'N/A'
        })

    attendance_records_qs = Attendance.objects.filter(
        student=student_profile
    ).select_related(
        'session__course'
    ).order_by('-date_time')

    attendance_records_data = []
    for record in attendance_records_qs:
        attendance_records_data.append({
            'course_name': record.session.course.course_name,
            'course_code': record.session.course.course_code,
            'date_time': record.date_time.isoformat(),
            'status': record.status,
            'image_data_url': record.image_data.url if record.image_data else None,
            'session_id': record.session.id,
            'session_day': record.session.get_day_of_week_display(),
            'session_start_time': record.session.start_time.strftime('%H:%M'),
        })

    enrolled_course_ids = [enrollment.course.course_code for enrollment in enrolled_courses_qs]

    class_schedule_qs = ClassSession.objects.filter(course__in=enrolled_course_ids).select_related(
        'course', 'lecturer__user'
    ).order_by('day_of_week', 'start_time')

    class_schedule_data = []
    for session in class_schedule_qs:
        class_schedule_data.append({
            'id': session.id,
            'course_name': session.course.course_name,
            'course_code': session.course.course_code,
            'day_of_week': session.get_day_of_week_display(),
            'start_time': session.start_time.strftime('%H:%M'),
            'end_time': session.end_time.strftime('%H:%M'),
            'room': session.room,
            'lecturer_name': session.lecturer.user.get_full_name() if session.lecturer else 'N/A',
        })

    enrollments = student_profile.enrollments.select_related('course__lecturer__user')
    lecturer_info = []
    for enrollment in enrollments:
        course = enrollment.course
        lecturer = course.lecturer
        if lecturer:
            lecturer_info.append({
                'course_code': course.course_code,
                'course_name': course.course_name,
                'lecturer_name': f"{lecturer.user.first_name} {lecturer.user.last_name}",
                'lecturer_email': lecturer.user.email,
            })

    context = {
        'student': {
            'firstName': user_data.first_name,
            'lastName': user_data.last_name,
            'email': user_data.email,
            'studentNumber': student_profile.user.username,
            'program': student_profile.program,
            'pk': user_data.pk,
        },
        'subjects': subjects_data,
        'attendance_records': attendance_records_data,
        'class_schedule': class_schedule_data,
        'lecturer_info': lecturer_info,
    }

     
    return render(request, 'students/student_dashboard.html', context)

@login_required
@user_passes_test(is_lecturer, login_url='/webapp/login/')
def lecturer_dashboard(request):
    """
    Displays the dashboard for a logged-in lecturer.
    Fetches lecturer-specific details, courses taught, and class sessions.
    """
    lecturer_profile = request.user.lecturer_profile
    user_data = request.user

    lecturer_context_data = {
        'firstName': user_data.first_name,
        'lastName': user_data.last_name,
        'email': user_data.email,
        'staffNumber': user_data.username,
        'department': lecturer_profile.department,
        'pk': user_data.pk,
    }
 
    lecturer_sessions_qs = ClassSession.objects.filter(
        lecturer=lecturer_profile
    ).select_related('course').order_by('day_of_week', 'start_time')

    # --- Upcoming Session Calculation ---
    upcoming_session = None
    now = timezone.localtime(timezone.now())  # Get the current local datetime
    today_date = now.date()                    # Extract today's date
    current_day_of_week_int = today_date.weekday()  
    current_time = now.time()                 # Get the current time

    # Mapping your model's day_of_week strings to Python's weekday() integers
    day_name_to_int = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
        'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    
    potential_upcoming_sessions = []

    for session in lecturer_sessions_qs:
        session_day_int = day_name_to_int.get(session.day_of_week)
        
        if session_day_int is not None:
            days_diff = session_day_int - current_day_of_week_int
            
            # Calculate days_ahead to the next occurrence of this session's day
            if days_diff < 0:
                # If the session's day has already passed this week (e.g., it's Thursday, session was Monday),
                # schedule for next week.
                days_ahead = days_diff + 7
            elif days_diff == 0:
                # If it's today, check if the session time has already passed.
                if session.start_time <= current_time:
                    # If time has passed or it's the current session, schedule for next week.
                    days_ahead = 7
                else:
                    # Session is today and still in the future.
                    days_ahead = 0
            else:
                # Session is on a future day this week.
                days_ahead = days_diff
            
            # Calculate the actual concrete date for this upcoming session.
            concrete_session_date = today_date + timedelta(days=days_ahead)

            potential_upcoming_sessions.append({
                'id': session.pk,
                'course': {
                    'subjectName': session.course.course_name,
                    'subjectCode': session.course.course_code,
                },
                'date': concrete_session_date,
                'time': session.start_time,
                'location': session.room,
                'day_of_week': session.day_of_week, # Include for full display if needed
            })
    
    # Sort all potential sessions by concrete date and then by time to find the very next one.
    if potential_upcoming_sessions:
        potential_upcoming_sessions.sort(key=lambda x: (x['date'], x['time']))
        upcoming_session = potential_upcoming_sessions[0] # This is the earliest upcoming session.

    # --- End Upcoming Session Calculation ---

    # --- Fetch unique courses taught by the lecturer  
    # This query directly gets the Course objects associated with the lecturer.
    courses_taught_qs = Course.objects.filter(lecturer=lecturer_profile).order_by('course_code')

    courses_for_dashboard_cards = []  
    for course in courses_taught_qs:
        courses_for_dashboard_cards.append({
            'subjectCode': course.course_code,
            'subjectName': course.course_name
        })
 
    enrolled_students_qs = Student.objects.filter(
        enrollments__course__in=courses_taught_qs
    ).distinct().select_related('user').prefetch_related(
        Prefetch(
            'enrollments',
            queryset=Enrollment.objects.filter(course__in=courses_taught_qs).select_related('course'),
            to_attr='lecturer_related_enrollments'
        )
    ).order_by('user__last_name', 'user__first_name')

    enrolled_students_data = []
    for student in enrolled_students_qs:
        student_courses_list = []
        for enrollment in student.lecturer_related_enrollments:
            student_courses_list.append({
                'subjectName': enrollment.course.course_name,
                'subjectCode': enrollment.course.course_code
            })
        enrolled_students_data.append({
            'firstName': student.user.first_name,
            'lastName': student.user.last_name,
            'studentNumber': student.user.username,
            'email': student.user.email,
            'program': student.program,
            'enrolled_courses': student_courses_list
        })

    attendance_records_qs = Attendance.objects.filter(
        session__in=lecturer_sessions_qs # sessions are filtered by lecturer in the first query
    ).select_related('student__user', 'session__course').order_by('-date_time')

    attendance_records_data = []
    for record in attendance_records_qs:
        attendance_records_data.append({
            'id': record.student.user.id,
            'student_firstName': record.student.user.first_name,
            'student_lastName': record.student.user.last_name,
            'student_studentNumber': record.student.user.username,
            'subjectName': record.session.course.course_name,
            'subjectCode': record.session.course.course_code,
            'dateAndTime': record.date_time.isoformat(),
            'status': record.status,
            'image_data_url': record.image_data.url if record.image_data else None,
        })

    context = {
        'lecturer': lecturer_context_data,
        'courses': courses_for_dashboard_cards, # This is the list of unique courses for the cards!
        'enrolled_students': enrolled_students_data,
        'attendance_records': attendance_records_data,
        'upcoming_session': upcoming_session, # This is the single upcoming session
    }
    return render(request, 'lecturers/lecture_dashboard.html', context)


@login_required
@user_passes_test(is_lecturer, login_url='/webapp/login/')
def view_course_sessions(request, course_code):
    """
    Displays all class sessions for a specific course taught by the logged-in lecturer.
    Each session's next concrete upcoming date is calculated for display.
    """
    lecturer_profile = request.user.lecturer_profile
    
    # Securely get the Course object. It must exist AND be taught by the current lecturer.
    course = get_object_or_404(Course, course_code=course_code, lecturer=lecturer_profile)

    # Fetch all class sessions for this specific course and lecturer.
    # Order them by day of the week and then by start time for a logical display.
    course_sessions_qs = ClassSession.objects.filter(
        course=course,
        lecturer=lecturer_profile
    ).order_by('day_of_week', 'start_time')

    sessions_for_display = []
    now = timezone.localtime(timezone.now()) # Get the current local datetime
    today = now.date()                       # Extract today's date
    current_day_of_week_int = today.weekday() # Get today's weekday as an integer (0=Monday, 6=Sunday)
    current_time = now.time()                # Get the current time

    # Map the string day names from your model to Python's integer weekdays
    day_name_to_int = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
        'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    
    for session in course_sessions_qs:
        session_day_int = day_name_to_int.get(session.day_of_week)
        
        if session_day_int is not None: # Ensure the day name is valid
            days_diff = session_day_int - current_day_of_week_int
            
            # Calculate how many days ahead the next occurrence of this session is
            if days_diff < 0:
                # If the session's day has already passed this week, it's next week
                days_ahead = days_diff + 7
            elif days_diff == 0:
                # If it's today, check if the session time has already passed
                if session.start_time <= current_time:
                    # If time has passed or it's the exact current session, schedule for next week
                    days_ahead = 7
                else:
                    # Session is today and still in the future
                    days_ahead = 0
            else:
                # Session is on a future day this week
                days_ahead = days_diff
            
            # Calculate the actual concrete date for this upcoming session instance
            upcoming_session_date = today + timedelta(days=days_ahead)

            sessions_for_display.append({
                'id': session.pk,
                'day_of_week': session.day_of_week,
                'date': upcoming_session_date,  
                'start_time': session.start_time,
                'end_time': session.end_time,
                'location': session.room,
                'course_name': course.course_name,  
                'course_code': course.course_code,  
            })
            
    # Finally, sort the prepared sessions by their calculated upcoming date, then by start time.
    sessions_for_display.sort(key=lambda x: (x['date'], x['start_time']))

    context = {
        'course': course,  # The course object for this session
        'course_sessions_list': sessions_for_display, # The list of sessions for this course
    }
    return render(request, 'lecturers/course_sessions_detail.html', context)




@login_required
@user_passes_test(is_lecturer, login_url='/webapp/login/')
def send_announcement(request):
    
    if not hasattr(request.user, 'lecturer_profile'):
        messages.error(request, "Access denied. You must be a lecturer to send announcements.")
        return redirect('lecturer_dashboard')  

    lecturer_profile = request.user.lecturer_profile
    
    # Get all courses taught by the current lecturer
    lecturer_courses = Course.objects.filter(lecturer=lecturer_profile).order_by('course_name')
    
    
    course_choices = [('', 'All My Modules')] + \
                     [(course.course_code, f"{course.course_name} ({course.course_code})") 
                      for course in lecturer_courses]

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        
        form.fields['course_code'].choices = course_choices 
        
        if form.is_valid():
            selected_course_code = form.cleaned_data['course_code']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            recipient_emails = set()  
            
            if selected_course_code:
                # Send to students of a specific course
                try:
                    course = lecturer_courses.get(course_code=selected_course_code)
                    
                
                    students_to_email = Student.objects.filter(enrollments__course=course).distinct() 
                    
                    for student in students_to_email:
                        if student.user and student.user.email:  
                            recipient_emails.add(student.user.email)
                except Course.DoesNotExist:
                    messages.error(request, "Selected course not found or you don't teach it.")
                    return render(request, 'lecturers/send_announcement.html', {'form': form})
            else:
                # Send to all students across all courses taught by the lecturer
                 
                students_to_email = Student.objects.filter(enrollments__course__in=lecturer_courses).distinct() # <--- FIXED THIS LINE
                
                for student in students_to_email:
                    if student.user and student.user.email:
                        recipient_emails.add(student.user.email)

            if not recipient_emails:
                messages.warning(request, "No students found to send the announcement to for the selected course(s). Please ensure students are enrolled.")
            else:
                
                html_content = render_to_string('emails/announcement_email.html', {
                    'subject': subject,
                    'message': message,
                    'lecturer_name': request.user.get_full_name() or request.user.username,
                    'course_info': selected_course_code if selected_course_code else 'All your courses'
                })
                text_content = strip_tags(html_content)  

                try:
                     
                    sender_email = request.user.email if request.user.email else 'nyikogiven74@gmail.com' # Fallback sender
                    sender_name = request.user.get_full_name() or request.user.username

                    msg = EmailMultiAlternatives(
                        subject,
                        text_content,
                        f"{sender_name} <{sender_email}>",  
                        list(recipient_emails)  
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    messages.success(request, f"Announcement sent successfully to {len(recipient_emails)} student(s).")
                    return redirect('lecturer_dashboard')  
                except Exception as e:
                    messages.error(request, f"Failed to send announcement: {e}. Check your email settings (settings.py) and ensure the sender email is valid.")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = AnnouncementForm()
        
        form.fields['course_code'].choices = course_choices 

    context = {
        'form': form,
    }
    return render(request, 'lecturers/send_announcement.html', context)



# --- Registration Views ---

def register_student(request):
    """
    Handles student registration.
    """
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        student_form = StudentForm(request.POST)
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = 'Student'
            user.save()
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            messages.success(request, "Student account created successfully! You can now log in.")
            return redirect('login')
    else:
        user_form = CustomUserCreationForm()
        student_form = StudentForm()

    context = {
        'user_form': user_form,
        'student_form': student_form
    }
    
    return render(request, 'register_student.html', context)


# --- Course Management Views (New) ---

@login_required
# Corrected login_url for the decorator
@user_passes_test(is_admin, login_url='/webapp/login/')
def course_list(request):
    """
    Displays a list of all courses.
    """
    courses = Course.objects.select_related('lecturer__user').all().order_by('course_code')
    context = {
        'courses': courses
    }
    
    return render(request, 'course_list.html', context)


@login_required
# Corrected login_url for the decorator
@user_passes_test(is_admin, login_url='/webapp/login/')
def add_course(request):
    """
    Handles adding a new course.
    """
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course added successfully!")
            return redirect('course_list')  
    else:
        form = CourseForm()
    context = {
        'form': form
    }
    
    return render(request, 'add_course.html', context)

@login_required

@user_passes_test(is_admin, login_url='/webapp/login/')
def enroll_student(request, student_id):
    """
    Handles enrolling a student into courses.
    This is a simplified view; you might want a more complex form for multiple courses.
    """
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = student
            # Check if enrollment already exists to prevent duplicates
            if not Enrollment.objects.filter(student=student, course=enrollment.course).exists():
                enrollment.save()
                messages.success(request, f"Student {student.user.username} enrolled in {enrollment.course.course_name} successfully!")
                return redirect('student_dashboard')  
                form.add_error(None, "Student is already enrolled in this course.")
                messages.warning(request, "Student is already enrolled in this course.")
    else:
        form = EnrollmentForm(initial={'student': student_id})  

    context = {
        'student': student,
        'form': form
    }
     
    return render(request, 'enroll_student.html', context)


# --- API Endpoints  

@login_required
@user_passes_test(is_student)
def update_student_profile_api(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            user = request.user
            student_profile = user.student_profile

            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            if data.get('email'):
                if User.objects.filter(email=data['email']).exclude(pk=user.pk).exists():
                    return JsonResponse({'error': 'Email already in use.'}, status=400)
                user.email = data['email']
            user.save()

            student_profile.program = data.get('program', student_profile.program)
            student_profile.save()

            return JsonResponse({'message': 'Profile updated successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@login_required
@user_passes_test(is_student)
def mark_attendance_api(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            session_id = data.get('session_id')
            image_data_b64 = data.get('image_data')

            if not session_id or not image_data_b64:
                return JsonResponse({'error': 'Missing session ID or image data.'}, status=400)

            session = get_object_or_404(ClassSession, pk=session_id)
            student = request.user.student_profile

            if ';base64,' in image_data_b64:
                format, imgstr = image_data_b64.split(';base64,')
                ext = format.split('/')[-1]
            else:
                imgstr = image_data_b64
                ext = 'png'
            image_data = base64.b64decode(imgstr)

            file_name = f"attendance_{student.user.username}_{session.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            content_file = ContentFile(image_data, name=file_name)

            current_time = timezone.now().time()
             
            if current_time <= session.start_time:
                attendance_status = 'Present'
            elif current_time > session.start_time and current_time <= session.end_time:
                attendance_status = 'Late'
            else:
                attendance_status = 'Absent'

            attendance_record, created = Attendance.objects.update_or_create(
                student=student,
                session=session,
                defaults={
                    'status': attendance_status,
                    'image_data': content_file,
                    'date_time': timezone.now()
                }
            )

            new_record_data = {
                'course_name': attendance_record.session.course.course_name,
                'course_code': attendance_record.session.course.course_code,
                'date_time': attendance_record.date_time.isoformat(),
                'status': attendance_record.status,
                'image_data_url': attendance_record.image_data.url if attendance_record.image_data else None,
                'session_id': attendance_record.session.id,
                'session_day': attendance_record.session.get_day_of_week_display(),
                'session_start_time': attendance_record.session.strftime('%H:%M'),
            }

            return JsonResponse({
                'message': 'Attendance marked successfully!',
                'status': attendance_record.status,
                'course_name': session.course.course_name,
                'new_record': new_record_data,
                'created': created
            })

        except ClassSession.DoesNotExist:
            return JsonResponse({'error': 'Class session not found.'}, status=404)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


 
@login_required
def add_class_session(request):
    """
    Handles the creation of a new class session.
    Only accessible by logged-in lecturers.
    """
    
    if not hasattr(request.user, 'lecturer_profile'):
        messages.error(request, "You must be a lecturer to add class schedules.")
        return redirect('lecturer_dashboard')  

     
    lecturer_profile = request.user.lecturer_profile

    if request.method == 'POST':
        
        form = ClassSessionForm(request.POST, lecturer_profile=lecturer_profile)
        if form.is_valid():
            class_session = form.save(commit=False)
            class_session.lecturer = lecturer_profile  
            class_session.save()
            messages.success(request, "Class session scheduled successfully!")
            return redirect('lecturer_dashboard') # Redirect to the lecturer's dashboard after success
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # For GET request, instantiate an empty form and pass the lecturer_profile
        form = ClassSessionForm(lecturer_profile=lecturer_profile)

    # Render the form template, passing the form instance
    return render(request, 'lecturers/class_session_form.html', {'form': form})

@login_required
def edit_class_session(request, pk):
    """
    Handles the editing of an existing class session.
    Only accessible by logged-in lecturers, and only for sessions they conduct.
    """
    # Ensure the logged-in user is a lecturer
    if not hasattr(request.user, 'lecturer_profile'):
        messages.error(request, "You must be a lecturer to edit class schedules.")
        return redirect('lecturer_dashboard')

    # Get the lecturer profile associated with the logged-in user
    lecturer_profile = request.user.lecturer_profile

    # Get the class session object, ensuring it belongs to the current lecturer
    class_session = get_object_or_404(ClassSession, pk=pk, lecturer=lecturer_profile)

    if request.method == 'POST':
        # Pass the lecturer_profile to the form's __init__ method
        form = ClassSessionForm(request.POST, instance=class_session, lecturer_profile=lecturer_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Class session updated successfully!")
            return redirect('lecturer_dashboard') # Redirect to dashboard after success
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # For GET request, instantiate the form with the existing instance data and pass the lecturer_profile
        form = ClassSessionForm(instance=class_session, lecturer_profile=lecturer_profile)

    # 
    return render(request, 'academics/class_session_form.html', {'form': form, 'class_session': class_session})


@login_required
@user_passes_test(is_student)
def download_attendance(request):
    student = request.user.student_profile
    attendance_records = student.attendance_records.select_related('session__course').all()

    # Get filters from query params
    date = request.GET.get('date')
    subject = request.GET.get('subject')

    if date:
        attendance_records = attendance_records.filter(date_time__date=date)
    if subject:
        attendance_records = attendance_records.filter(session__course__course_name=subject)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

    writer = csv.writer(response)
    writer.writerow(['Course', 'Date/Time', 'Status'])

    for record in attendance_records:
        writer.writerow([
            record.session.course.course_name,
            record.date_time.strftime('%Y-%m-%d %H:%M'),
            record.status
        ])
    return response

@login_required
def download_timetable(request):
    student = request.user.student_profile
    courses = student.enrollments.all().select_related('course')
    sessions = ClassSession.objects.filter(course__in=[e.course for e in courses]).select_related('course', 'lecturer')

    timetable = [['Course', 'Day', 'Start Time', 'End Time', 'Room', 'Lecturer']]
    for session in sessions:
        timetable.append([
            session.course.course_name,
            session.day_of_week,
            session.start_time.strftime('%H:%M'),
            session.end_time.strftime('%H:%M'),
            session.room,
            f"{session.lecturer.user.first_name} {session.lecturer.user.last_name}"
        ])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="timetable.csv"'
    writer = csv.writer(response)
    for row in timetable:
        writer.writerow(row)
    return response

@login_required
def contact_lecturers(request):
    student = request.user.student_profile  # Get the Student profile for the logged-in user
    # Get all enrollments for this student
    enrollments = student.enrollments.select_related('course__lecturer__user')
    # Build a list of lecturer info for each enrolled course
    lecturer_info = []
    for enrollment in enrollments:
        course = enrollment.course
        lecturer = course.lecturer
        if lecturer:
            lecturer_info.append({
                'course_code': course.course_code,
                'course_name': course.course_name,
                'lecturer_name': f"{lecturer.user.first_name} {lecturer.user.last_name}",
                'lecturer_email': lecturer.user.email,
            })
    return render(request, 'students/contact_lecturers.html', {'lecturer_info': lecturer_info})