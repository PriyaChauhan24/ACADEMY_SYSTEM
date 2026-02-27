from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# --- 1. Custom User Model ---
class User(AbstractUser):
    BRANCH_CHOICES = [
        ('CE', 'Computer Engineering'),
        ('IT', 'Information Technology'),
    ]
    SEM_CHOICES = [(i, f'Semester {i}') for i in range(1, 9)]
    
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    
    # New Academic Fields
    branch = models.CharField(max_length=5, choices=BRANCH_CHOICES, null=True, blank=True)
    semester = models.IntegerField(choices=SEM_CHOICES, default=1)
    enrollment_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.branch} - Sem {self.semester})"

# --- 2. Student Data & AI Biometrics ---
class StudentData(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    face_encoding = models.BinaryField(null=True, blank=True) # AI Face ID storage
    attendance = models.FloatField(default=0.0)
    marks = models.IntegerField(default=0)
    performance = models.CharField(max_length=20, default="Pending")
    performance_summary = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True) # Tracks if student is still in college

    def save(self, *args, **kwargs):
        # Automated Performance Logic
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
        return f"{self.student.enrollment_number} - Sem {self.student.semester}"

# --- 3. Study Materials (PDFs & Video Links) ---
class Material(models.Model):
    title = models.CharField(max_length=255)
    # We can now filter materials by branch/semester
    branch = models.CharField(max_length=5, choices=User.BRANCH_CHOICES, null=True, blank=True)
    semester = models.IntegerField(choices=User.SEM_CHOICES, default=1)
    file = models.FileField(upload_to='materials/pdfs/', null=True, blank=True)
    video_link = models.URLField(null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.branch} Sem {self.semester})"

# --- 4. Assignment Submissions ---
class AssignmentSubmission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment_name = models.CharField(max_length=255)
    submission_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.assignment_name}"

# --- 5. Live Sessions ---
class LiveSession(models.Model):
    title = models.CharField(max_length=200, default="Today's Live Class")
    meeting_link = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title