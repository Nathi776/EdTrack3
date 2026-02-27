# academics/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Student, Lecturer, Course, Enrollment, ClassSession, Attendance



class AnnouncementForm(forms.Form):
    
    course_code = forms.ChoiceField(
        label="Select Course (or leave blank for all your Modules)",
        required=False,
        choices=[],  
        widget=forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'})
    )
    
    subject = forms.CharField(
        label="Subject",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'placeholder': 'e.g., Class Cancellation: DBP316D'})
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={'rows': 8, 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'placeholder': 'Dear students, please be advised that...'}),
        help_text="Write your announcement here. It will be sent to all students enrolled in the selected course(s)."
    )








# --- 1. User Forms (for custom User model) ---

class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users, with all the fields from our custom User model.
    Inherits from Django's UserCreationForm for handling password hashing and verification.
    """
    class Meta:
        model = User
 
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        pass

class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating existing users, with all the fields from our custom User model.
    Inherits from Django's UserChangeForm.
    """
    class Meta:
        model = User
        
        fields = '__all__'  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
      
        pass


# --- 2. Student Form ---
class StudentForm(forms.ModelForm):
    """
    Form for creating and updating Student profiles.
    Note: The 'user' field (the OneToOneField) is typically handled separately
    when creating a new student, often by creating the User first and then the Student profile.
    For existing students, this form can be used to update their profile specific details.
    """
    class Meta:
        model = Student
  
        exclude = ('user',)
       
        labels = {
            'program': 'Academic Program',
            'parent_email': 'Parent/Guardian Email',
            'parent_phone_num': 'Parent/Guardian Phone Number',
        }
        widgets = {
            'program': forms.TextInput(attrs={'placeholder': 'e.g., Computer Science'}),
            'parent_email': forms.EmailInput(attrs={'placeholder': 'parent@mail.com'}),
            'parent_phone_num': forms.TextInput(attrs={'placeholder': '+27123456789'}),
        }


# --- 3. Lecturer Form ---
class LecturerForm(forms.ModelForm):
    """
    Form for creating and updating Lecturer profiles.
    Similar to StudentForm, the 'user' field is typically excluded.
    """
    class Meta:
        model = Lecturer
        exclude = ('user',)
   
        labels = {
            'department': 'Department',
        }
        widgets = {
            'department': forms.TextInput(attrs={'placeholder': 'e.g., Electrical Engineering'}),
        }


# --- 4. Course Form ---
class CourseForm(forms.ModelForm):
    """
    Form for creating and updating Courses.
    """
    class Meta:
        model = Course
        fields = '__all__'  
        labels = {
            'course_code': 'Course Code',
            'course_name': 'Course Name',
            'lecturer': 'Assigned Lecturer',
        }
        widgets = {
            'course_code': forms.TextInput(attrs={'placeholder': 'e.g., CSC101'}),
            'course_name': forms.TextInput(attrs={'placeholder': 'e.g., Introduction to Programming'}),
        }


# --- 5. Enrollment Form ---
class EnrollmentForm(forms.ModelForm):
    """
    Form for managing student enrollments in courses.
    """
    class Meta:
        model = Enrollment
        fields = '__all__'  
        labels = {
            'student': 'Student',
            'course': 'Course',
            'enrollment_date': 'Enrollment Date',
        }
        widgets = {
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}), # HTML5 date picker
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
      
        pass


# --- 6. ClassSession Form ---
class ClassSessionForm(forms.ModelForm):
    """
    Form for scheduling and updating class sessions.
    """
    class Meta:
        model = ClassSession
        exclude = ['lecturer']  
        labels = {
            'day_of_week': 'Day of Week',
            'start_time': 'Start Time',
            'end_time': 'End Time',
        }
        widgets = {
            'day_of_week': forms.Select(choices=ClassSession.day_of_week.field.choices),  
            'start_time': forms.TimeInput(attrs={'type': 'time'}),  
            'end_time': forms.TimeInput(attrs={'type': 'time'}),    
            'room': forms.TextInput(attrs={'placeholder': 'e.g., Room A101, Zoom Link'}),
        }
 
    def __init__(self, *args, **kwargs):
        #  
        self.lecturer_profile = kwargs.pop('lecturer_profile', None)
        super().__init__(*args, **kwargs)

 
        if self.lecturer_profile:
             self.fields['course'].queryset = Course.objects.filter(lecturer=self.lecturer_profile)

# --- 7. Attendance Form ---
class AttendanceForm(forms.ModelForm):
    """
    Form for recording student attendance for sessions.
    """
    class Meta:
        model = Attendance
 
        fields = ('student', 'session', 'status', 'image_data')
        labels = {
            'student': 'Student',
            'session': 'Class Session',
            'status': 'Attendance Status',
            'image_data': 'Verification Image',
        }
        widgets = {
            'status': forms.Select(choices=Attendance.status.field.choices),
        }
    
    
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        session = cleaned_data.get('session')

      
        if self.instance is None and student and session:  
            if Attendance.objects.filter(student=student, session=session).exists():
                raise forms.ValidationError("This student's attendance for this session has already been recorded.")
        return cleaned_data