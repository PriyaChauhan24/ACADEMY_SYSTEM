from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    enrollment_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

class Material(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='materials/')
    video_link = models.URLField(blank=True, null=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

class StudentData(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'is_student': True})
    attendance = models.FloatField(default=0.0)
    marks = models.IntegerField(default=0)
    performance = models.CharField(max_length=20, default="Average")

    def __str__(self):
        return self.student.username
    
class StudentData(models.Model):
    student = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    face_encoding = models.BinaryField(blank=True, null=True)
    attendance = models.FloatField(default=0.0)
    marks = models.IntegerField(default=0)
    performance = models.CharField(max_length=20, default="Pending")

    def save(self, *args, **kwargs):
        # Automatic Performance Logic
        if self.marks >= 80:
            self.performance = "Excellent"
        elif self.marks >= 60:
            self.performance = "Good"
        elif self.marks >= 40:
            self.performance = "Average"
        else:
            self.performance = "Poor"
        
        super(StudentData, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.performance}"
    
    def __str__(self):
        return f"{self.student.username}'s Data"

class AssignmentSubmission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment_name = models.CharField(max_length=200)
    submission_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.assignment_name}"
    
class LiveSession(models.Model):
    title = models.CharField(max_length=200, default="Today's Live Class")
    meeting_link = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class StudentData(models.Model):
    # ... your existing fields (attendance, marks, etc.) ...
    face_encoding = models.BinaryField(null=True, blank=True) # Stores the 128 AI measurements


