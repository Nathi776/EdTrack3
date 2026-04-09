
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- Authentication URLs ---
    path('', views.custom_login_view, name='login'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),

    # --- Dashboard URLs ---
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('student/face-setup/', views.student_face_setup, name='student_face_setup'),
    path('dashboard/lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),

    # --- Other existing URLs ---
    path('register/student/', views.register_student, name='register_student'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.add_course, name='add_course'),
    path('enroll/<int:student_id>/', views.enroll_student, name='enroll_student'),


    # --- Session urls---
    path('lecturer/schedule/add/', views.add_class_session, name='add_class_session'),
    path('lecturer/schedule/edit/<int:pk>/', views.edit_class_session, name='edit_class_session'),

     path('lecturer/course/<str:course_code>/', views.view_course_sessions, name='view_course_sessions'),

    # --- announcements urls---
    path('announcements/send/', views.send_announcement, name='send_announcement'),

    # --- Custom admin portal pages ---
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/students/', views.admin_dashboard, name='manage-students'),
    path('admin-panel/students/add/', views.add_student, name='add_student'),
    path('admin-panel/students/<str:username>/edit/', views.edit_student, name='edit_student'),
    path('admin-panel/students/<str:username>/delete/', views.delete_student, name='delete_student'),
    path('admin-panel/lecturers/add/', views.add_lecturer, name='add_lecturer'),
    path('admin-panel/lecturers/<str:username>/edit/', views.edit_lecturer, name='edit_lecturer'),
    path('admin-panel/lecturers/<str:username>/delete/', views.delete_lecturer, name='delete_lecturer'),
    path('admin-panel/courses/', views.course_list, name='course_list'),
    path('admin-panel/courses/add/', views.add_course, name='add_course'),
    path('admin-panel/courses/<str:course_code>/edit/', views.edit_course, name='edit_course'),
    path('admin-panel/courses/<str:course_code>/delete/', views.delete_course, name='delete_course'),
    path('admin-panel/class-sessions/', views.classsession_list, name='classsession_list'),
    path('admin-panel/class-sessions/add/', views.add_class_session_admin, name='add_class_session_admin'),
    path('admin-panel/class-sessions/<int:pk>/edit/', views.edit_class_session_admin, name='edit_class_session_admin'),
    path('admin-panel/class-sessions/<int:pk>/delete/', views.delete_class_session, name='delete_class_session'),
    path('admin-panel/enrollments/', views.enrollment_list, name='enrollment_list'),
    path('admin-panel/enrollments/add/', views.add_enrollment, name='add_enrollment'),
    path('admin-panel/enrollments/<int:pk>/edit/', views.edit_enrollment, name='edit_enrollment'),
    path('admin-panel/enrollments/<int:pk>/delete/', views.delete_enrollment, name='delete_enrollment'),
    path('admin-panel/students/<int:student_id>/enroll/', views.enroll_student, name='admin_enroll_student'),
    path('admin-panel/attendance/', views.attendance_list, name='attendance_list'),
    path('admin-panel/attendance/add/', views.add_attendance, name='add_attendance'),
    path('admin-panel/attendance/<int:pk>/edit/', views.edit_attendance, name='edit_attendance'),
    path('admin-panel/attendance/<int:pk>/delete/', views.delete_attendance, name='delete_attendance'),

    # --- API Endpoints ---
    path('api/update-student-profile/', views.update_student_profile_api, name='update_student_profile_api'),
    path('api/enroll-face/', views.enroll_face_api, name='enroll_face_api'),
    path('api/mark-attendance/', views.mark_attendance_api, name='mark_attendance_api'),
    # helper used by student dashboard JS before opening the attendance modal
    path('api/check-attendance/<int:session_id>/', views.check_attendance_status, name='check_attendance_status'),

    # --- Download timetable and Records ---
    path('student/download-timetable/', views.download_timetable, name='download_timetable'),
    path('student/download-attendance/', views.download_attendance, name='download_attendance'),
     
    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # --- Contact URLs ---
    path('contact-lecturers/', views.contact_lecturers, name='contact_lecturers'),
]