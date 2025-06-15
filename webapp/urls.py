
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
    # --- API Endpoints ---
    path('api/update-student-profile/', views.update_student_profile_api, name='update_student_profile_api'),
    path('api/mark-attendance/', views.mark_attendance_api, name='mark_attendance_api'),

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