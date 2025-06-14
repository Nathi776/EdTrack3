 

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import IntegrityError  
from django.contrib import messages

from .models import User, Student, Lecturer, Course, Enrollment, ClassSession, Attendance

class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Profile'
    fk_name = 'user'

class LecturerInline(admin.StackedInline):
    model = Lecturer
    can_delete = False
    verbose_name_plural = 'Lecturer Profile'
    fk_name = 'user'

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'user_type')}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
        }),
    )

    inlines = [StudentInline, LecturerInline]

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        
        if obj.user_type == 'Student':
            return [StudentInline(self.model, self.admin_site)]
        elif obj.user_type == 'Lecturer':
            return [LecturerInline(self.model, self.admin_site)]
        return []

    def save_model(self, request, obj, form, change):
        # Save the User object first
        super().save_model(request, obj, form, change)

        if change: # If an existing user is being modified
            old_user_type = User.objects.get(pk=obj.pk).user_type
            new_user_type = obj.user_type

            if old_user_type != new_user_type:
                # Try to delete the old profile (if it exists and matches old_user_type)
                try:
                    if old_user_type == 'Student' and hasattr(obj, 'student_profile'):
                        obj.student_profile.delete()
                        messages.info(request, f"Old Student profile deleted for {obj.username}.")
                    elif old_user_type == 'Lecturer' and hasattr(obj, 'lecturer_profile'):
                        obj.lecturer_profile.delete()
                        messages.info(request, f"Old Lecturer profile deleted for {obj.username}.")
                except Exception as e:
                    messages.error(request, f"Error deleting old profile ({old_user_type}) for {obj.username}: {e}")

                # Attempt to create the new profile only if it doesn't already exist
                if new_user_type == 'Student' and not hasattr(obj, 'student_profile'):
                    try:
                        Student.objects.create(user=obj)
                        messages.success(request, f"New Student profile created for {obj.username}.")
                    except IntegrityError:
                        messages.warning(request, f"A Student profile for {obj.username} already exists (IntegrityError).")
                    except Exception as e:
                        messages.error(request, f"Error creating new Student profile for {obj.username}: {e}")
                elif new_user_type == 'Lecturer' and not hasattr(obj, 'lecturer_profile'):
                    try:
                        Lecturer.objects.create(user=obj)
                        messages.success(request, f"New Lecturer profile created for {obj.username}.")
                    except IntegrityError:
                        messages.warning(request, f"A Lecturer profile for {obj.username} already exists (IntegrityError).")
                    except Exception as e:
                        messages.error(request, f"Error creating new Lecturer profile for {obj.username}: {e}")
                elif new_user_type == 'Admin':
                    messages.info(request, f"User type for {obj.username} set to Admin.")

        else:  
              
            # If this is a new user, create the appropriate profile based on user_type
            if obj.user_type == 'Student' and not hasattr(obj, 'student_profile'):
                try:
                    Student.objects.create(user=obj)
                    messages.success(request, f"Initial Student profile created for {obj.username}.")
                except IntegrityError:
                    messages.warning(request, f"Student profile for {obj.username} already exists (IntegrityError during initial create).")
                except Exception as e:
                    messages.error(request, f"Error creating initial Student profile for {obj.username}: {e}. Check if Student model has required fields other than 'user'.")
            elif obj.user_type == 'Lecturer' and not hasattr(obj, 'lecturer_profile'):
                try:
                    Lecturer.objects.create(user=obj)
                    messages.success(request, f"Initial Lecturer profile created for {obj.username}.")
                except IntegrityError:
                    messages.warning(request, f"Lecturer profile for {obj.username} already exists (IntegrityError during initial create).")
                except Exception as e:
                    messages.error(request, f"Error creating initial Lecturer profile for {obj.username}: {e}. Check if Lecturer model has required fields other than 'user'.")
             

 
admin.site.register(User, CustomUserAdmin)

 
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(ClassSession)
admin.site.register(Attendance)