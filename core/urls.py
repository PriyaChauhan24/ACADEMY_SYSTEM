from django.urls import path
from . import views

urlpatterns = [
    # Login & Dashboards
    path('login/', views.login_view, name='login'),
    path('student/', views.student_dash, name='student_dash'),
    path('teacher-dash/', views.teacher_dash, name='teacher_dash'),
    
    # Academic Features
    path('update-marks/<int:student_id>/', views.update_marks, name='update_marks'),
    path('submit-hw/', views.submit_assignment, name='submit_assignment'),
    path('view-submissions/', views.view_submissions, name='view_submissions'),
    
    # Biometric Features (Renamed to match your upgraded views.py)
    path('face-login/', views.face_login, name='face_login'),
    path('register-face/', views.register_face, name='register_face'),
    path('verify-for-class/', views.verify_for_class, name='verify_for_class'),

    path('system-admin/', views.admin_dashboard, name='admin_dash'),
    path('reset-face/<int:student_id>/', views.reset_face_id, name='reset_face_id'),
    path('register/', views.register_student, name='register'),
    path('processing-biometrics/', views.processing_biometrics, name='processing_biometrics'),
]

