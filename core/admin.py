from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import User, Material, StudentData

# This tells Django to show your Custom User in the Admin
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_student', 'is_teacher', 'enrollment_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_student', 'is_teacher', 'enrollment_number')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Material)
admin.site.register(StudentData)
