from django.urls import path
from . import views

urlpatterns = [
    # --- Home/Landing Redirect ---
    # Redirects the base URL to the login page
    path('', views.login_view, name='home'),

    # --- Login & Registration ---
    path('login/', views.login_view, name='login'),
    path('register/', views.register_student, name='register'),
    path('processing-biometrics/', views.processing_biometrics, name='processing_biometrics'),
    
    # --- Dashboards ---
    path('dashboard/', views.student_dash, name='student_dash'),
    path('teacher-dash/', views.teacher_dash, name='teacher_dash'),
    path('system-admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # --- Academic Features ---
    path('update-marks/<int:student_id>/', views.update_marks, name='update_marks'),
    path('submit-hw/', views.submit_assignment, name='submit_assignment'),
    path('view-submissions/', views.view_submissions, name='view_submissions'),
    
    # --- AI Biometric Features ---
    path('face-login/', views.face_login, name='face_login'),
    path('register-face/', views.register_face, name='register_face'),
    path('verify-for-class/', views.verify_for_class, name='verify_for_class'),
    path('reset-face/<int:student_id>/', views.reset_face_id, name='reset_face_id'),
]