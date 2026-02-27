import cv2
import face_recognition
import numpy as np
import pickle
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, StudentData, Material, AssignmentSubmission, LiveSession
from .forms import StudentRegistrationForm

# --- 1. AUTHENTICATION & REGISTRATION ---

def login_view(request):
    if request.method == "POST":
        enrollment = request.POST.get('enrollment')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = None
        if enrollment:
            try:
                user_obj = User.objects.get(enrollment_number=enrollment)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                messages.error(request, "Invalid Enrollment Number")
        elif username:
            user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('student_dash' if user.is_student else 'teacher_dash')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'core/login.html')

def register_student(request):
    """Step 1: Account Creation and redirect to Processing Screen"""
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_student = True
            user.save()
            # Create a StudentData profile immediately for the new user
            StudentData.objects.create(student=user)
            login(request, user)
            messages.success(request, "Account created! Initializing Biometrics...")
            return redirect('processing_biometrics')
    else:
        form = StudentRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def face_login(request):
    """AI Login using Face Recognition."""
    video_capture = cv2.VideoCapture(0)
    found_user = None
    registered_students = StudentData.objects.exclude(face_encoding__isnull=True)
    known_encodings = []
    student_ids = []
    
    for sd in registered_students:
        known_encodings.append(pickle.loads(sd.face_encoding))
        student_ids.append(sd.student.id)

    while True:
        ret, frame = video_capture.read()
        if not ret: break
        
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            if True in matches:
                first_match_index = matches.index(True)
                user_id = student_ids[first_match_index]
                found_user = User.objects.get(id=user_id)
                break
        
        cv2.imshow('AI Login - Scanning...', frame)
        if found_user or cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

    if found_user:
        login(request, found_user)
        messages.success(request, f"Welcome back, {found_user.username}!")
        return redirect('student_dash')
    
    messages.error(request, "Face not recognized.")
    return redirect('login')


# --- 2. DASHBOARDS ---

@login_required
def student_dash(request):
    """Dashboard with Progress Bar calculation (Cleaned up duplicates)."""
    # Fetch data safely using .filter().first()
    data = StudentData.objects.filter(student=request.user).first()
    materials = Material.objects.all()
    live_class = LiveSession.objects.filter(is_active=True).first()
    
    # Logic for progress bar calculation
    progress = 25 # Initial progress for account creation
    if data:
        if data.face_encoding:
            progress += 35 # Extra for face registration
        if data.attendance > 0:
            progress += 40 # Extra for attending class
            
    # Cap at 100%
    progress = min(progress, 100)
        
    return render(request, 'core/student_dash.html', {
        'data': data, 
        'materials': materials, 
        'live_class': live_class,
        'progress': progress,
        'user': request.user
    })

@login_required
def teacher_dash(request):
    if not request.user.is_teacher: return redirect('login')
    if request.method == "POST":
        if 'meeting_link' in request.POST:
            LiveSession.objects.update_or_create(id=1, defaults={
                'meeting_link': request.POST.get('meeting_link'), 
                'is_active': True,
                'title': "Live Class"
            })
            messages.success(request, "Live session link updated!")
        elif 'title' in request.POST:
            Material.objects.create(
                title=request.POST.get('title'), 
                file=request.FILES.get('file'), 
                video_link=request.POST.get('video_url'), 
                teacher=request.user
            )
            messages.success(request, "Material uploaded!")
        return redirect('teacher_dash')
    return render(request, 'core/teacher_dash.html', {'students': StudentData.objects.all()})

@login_required
def admin_dashboard(request):
    """Note: Ensure your URL points here for 'admin_dash' name."""
    if not request.user.is_staff:
        messages.error(request, "Admins Only!")
        return redirect('login')
    
    context = {
        'total_students': StudentData.objects.count(),
        'registered_faces': StudentData.objects.exclude(face_encoding__isnull=True).count(),
        'active_sessions': LiveSession.objects.filter(is_active=True).count(),
        'students': StudentData.objects.all()
    }
    return render(request, 'core/admin_dash.html', context)


# --- 3. AI BIOMETRICS & FLOWS ---

@login_required
def processing_biometrics(request):
    """The Loading Page between Registration and Camera."""
    return render(request, 'core/processing_biometrics.html')

@login_required
def register_face(request):
    """Step 2: Biometric Enrollment."""
    video_capture = cv2.VideoCapture(0)
    encoding = None
    while True:
        ret, frame = video_capture.read()
        if not ret: break
        
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        if face_locations:
            encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            top, right, bottom, left = face_locations[0]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected! Press 'S' to Save", (left, top-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imshow("Initial Biometric Enrollment", frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('s') and encoding is not None:
            # Update existing data profile
            student_data, created = StudentData.objects.get_or_create(student=request.user)
            student_data.face_encoding = pickle.dumps(encoding)
            student_data.save()
            messages.success(request, "Biometrics saved! Welcome to the Academy.")
            break
        elif key & 0xFF == ord('q'): break

    video_capture.release()
    cv2.destroyAllWindows()
    return redirect('student_dash')

@login_required
def verify_for_class(request):
    """Face verification before joining Live Class."""
    student_data = StudentData.objects.filter(student=request.user).first()
    if not student_data or not student_data.face_encoding:
        messages.error(request, "Face not registered.")
        return redirect('student_dash')

    stored_encoding = pickle.loads(student_data.face_encoding)
    video_capture = cv2.VideoCapture(0)
    verified = False
    
    for _ in range(80):
        ret, frame = video_capture.read()
        if not ret: break
        
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            if True in face_recognition.compare_faces([stored_encoding], face_encoding, tolerance=0.5):
                verified = True
                break
        cv2.imshow('Verifying Identity...', frame)
        if verified or cv2.waitKey(1) & 0xFF == ord('q'): break

    video_capture.release()
    cv2.destroyAllWindows()

    if verified:
        student_data.attendance += 1.0
        student_data.save()
        live_class = LiveSession.objects.filter(is_active=True).first()
        if live_class: return redirect(live_class.meeting_link)
    
    messages.error(request, "Verification Failed.")
    return redirect('student_dash')


# --- 4. DATA MANAGEMENT ---

@login_required
def update_marks(request, student_id):
    if request.method == "POST":
        sr = get_object_or_404(StudentData, id=student_id)
        sr.marks = int(request.POST.get('marks', 0))
        sr.attendance = float(request.POST.get('attendance', 0.0))
        sr.save()
        messages.success(request, "Records Updated.")
    return redirect('teacher_dash')

@login_required
def submit_assignment(request):
    if request.method == "POST":
        AssignmentSubmission.objects.create(
            student=request.user, 
            assignment_name=request.POST.get('assignment_name'), 
            submission_file=request.FILES.get('assignment_file')
        )
        messages.success(request, "Submitted!")
        return redirect('student_dash')
    return render(request, 'core/submit_hw.html')

@login_required
def view_submissions(request):
    """View for teachers to see student uploads."""
    if not request.user.is_teacher: return redirect('login')
    submissions = AssignmentSubmission.objects.all().order_by('-submitted_at')
    return render(request, 'core/view_submissions.html', {'submissions': submissions})

@login_required
def reset_face_id(request, student_id):
    """Admin tool to clear biometric data."""
    if not request.user.is_staff:
        messages.error(request, "Unauthorized.")
        return redirect('login')
    student_record = get_object_or_404(StudentData, id=student_id)
    student_record.face_encoding = None
    student_record.save()
    messages.success(request, f"Biometric data for {student_record.student.username} reset.")
    return redirect('admin_dashboard')