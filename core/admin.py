from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Material, StudentData, AssignmentSubmission, LiveSession

# --- 1. Bulk Action: Promote Students to Next Semester ---
@admin.action(description='Promote selected students to next semester')
def promote_students(modeladmin, request, queryset):
    updated = 0
    for user in queryset:
        if user.is_student and user.semester < 8:
            user.semester += 1
            user.save()
            updated += 1
    modeladmin.message_user(request, f"Successfully promoted {updated} students.")

# --- 2. Custom User Admin ---
class CustomUserAdmin(UserAdmin):
    # This adds the "Promote" button to the "Action" dropdown
    actions = [promote_students]
    
    # Columns to show in the list view
    list_display = ('username', 'enrollment_number', 'branch', 'semester', 'is_student', 'is_teacher')
    
    # Sidebar filters for bulk management
    list_filter = ('branch', 'semester', 'is_student', 'is_teacher')
    
    # Search box for finding students by Enrollment or Name
    search_fields = ('username', 'enrollment_number')

    # Adding our custom fields to the edit screens
    fieldsets = UserAdmin.fieldsets + (
        ('Academic Info', {'fields': ('is_student', 'is_teacher', 'enrollment_number', 'branch', 'semester')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Academic Info', {'fields': ('is_student', 'is_teacher', 'enrollment_number', 'branch', 'semester')}),
    )

# --- 3. Better Management for Other Models ---

class StudentDataAdmin(admin.ModelAdmin):
    list_display = ('student', 'performance', 'marks', 'attendance')
    list_filter = ('performance', 'student__branch', 'student__semester')
    search_fields = ('student__username', 'student__enrollment_number')

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'branch', 'semester', 'uploaded_at')
    list_filter = ('branch', 'semester')

# --- 4. Register Everything ---
admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentData, StudentDataAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(AssignmentSubmission)
admin.site.register(LiveSession)