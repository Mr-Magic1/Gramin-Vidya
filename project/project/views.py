from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from student.models import Student
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import face_recognition
import numpy as np
import base64
from django.core.files.base import ContentFile

@login_required(login_url='login')
def home(request):
    return render(request,'dashboard.html')

@login_required(login_url='login')
def dashboard(request):
    today = timezone.now().date()
    total_students = Student.objects.count()
    present_count = Student.objects.filter(last_present=today).count()
    meal_count = present_count
    percentage = int((present_count / total_students) * 100) if total_students else 0

    context = {
        'date': today,
        'total_students': total_students,
        'present_count': present_count,
        'meal_count': meal_count,
        'percentage': percentage
    }
    return render(request, "dashboard.html", context)

@login_required(login_url='login')
def submit_student(request):
    reply = "Error Occured"
    if request.method == "POST":
        name = request.POST.get('name')
        clas = request.POST.get('class')
        roll = request.POST.get('rollNo')
        address = request.POST.get('address')
        guardian = request.POST.get('guardian')
        img = request.FILES.get('student_img')

        data = Student(
            name=name,
            clas=clas,
            roll=roll,
            address=address,
            guard=guardian,
            student_img=img
        )
        data.save()
        reply = "Data uploaded successfully"
    return render(request, 'add_student.html', {'reply': reply})

@login_required(login_url='login')
def attendance(request):
    students = []
    
    # Filter based on user (Teacher)
    if request.user.username == "shrey":
        students = Student.objects.filter(clas__icontains=5)
    elif request.user.username == "Khushboo":
        students = Student.objects.filter(clas__icontains=4)
    else:
        # Default fallback if user matches neither
        students = Student.objects.all()

    # Search Logic
    if request.method == "GET":
        clas_search = request.GET.get('classsearch')
        name_search = request.GET.get('namesearch')
        
        if clas_search:              
            students = students.filter(clas__icontains=clas_search)
        if name_search:
            students = students.filter(name__icontains=name_search)
    
    # Process students to check if they are present today
    student_list = []
    today = timezone.now().date()
    
    for s in students:
        status = 'absent'
        if s.last_present == today:
            status = 'present'
            
        student_list.append({
            'student': s,
            'name': s.name,
            'roll': s.roll,
            'clas': s.clas,
            'status': status
        })

    return render(request, 'attendance.html', {'students': student_list})

@login_required(login_url='login')
def add_student(request):
    return render(request,'add_student.html')


# --- NEW FACE RECOGNITION LOGIC ---

@csrf_exempt
def scan_face_attendance(request):
    """
    Receives a Base64 image from the frontend, identifies the student,
    and marks them present for today.
    """
    if request.method == 'POST':
        try:
            # 1. Get the image from POST data
            image_data = request.POST.get('image')
            
            # 2. Decode base64 to image
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            
            # 3. Load the uploaded image using face_recognition
            unknown_image = face_recognition.load_image_file(data)
            
            # 4. Generate encoding for the uploaded face
            # We take the first face found ([0])
            unknown_encodings = face_recognition.face_encodings(unknown_image)
            
            if len(unknown_encodings) == 0:
                return JsonResponse({'success': False, 'message': 'No face detected in camera frame.'})
            
            unknown_encoding = unknown_encodings[0]

            # 5. Compare with all students in DB
            # Note: In production, you would cache these encodings rather than loading images every time.
            students = Student.objects.exclude(student_img='')
            
            for student in students:
                try:
                    # Load student's saved reference image
                    known_image = face_recognition.load_image_file(student.student_img.path)
                    known_encoding = face_recognition.face_encodings(known_image)[0]
                    
                    # Compare
                    results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
                    
                    if results[0]:
                        # Match Found! Mark attendance.
                        student.last_present = timezone.now().date()
                        student.save()
                        return JsonResponse({
                            'success': True, 
                            'message': f'Attendance marked for {student.name}',
                            'student_name': student.name
                        })
                except Exception as e:
                    # Skip students with bad images or no faces in reference image
                    continue

            return JsonResponse({'success': False, 'message': 'Face not recognized.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


# --- RESULT & AUTH VIEWS (Kept same mostly) ---

@login_required(login_url='login')
def result(request):
    return render(request,'result.html')

from result.models import Result 
@login_required(login_url='login')
def update_result(request):
    reply="Error Occured"
    if request.method=="POST":   
        name=request.POST.get('name'),
        data=Result(
            name=request.POST.get('name'),
            clas=request.POST.get('clas'),
            roll=request.POST.get('roll'),
            guard=request.POST.get('guard'),
            hmath=request.POST.get('hmath'),
            hsci=request.POST.get('hsci'),
            hhis=request.POST.get('hhis'),
            heng=request.POST.get('heng'),
            hhindi=request.POST.get('hhindi'),
            fmath=request.POST.get('fmath'),
            fsci=request.POST.get('fsci'),
            fhis=request.POST.get('fhis'),
            feng=request.POST.get('feng'),
            fhindi=request.POST.get('fhindi'),
        )
        data.save()
        reply=f"Result of {name} uploaded successfully"
    return render(request,'result.html',{'reply':reply})

@login_required(login_url='login')
def show_result(request):
    results = Result.objects.all()
    # (Your existing calculation logic here...)
    # I am truncating the calculation part for brevity, keep your existing logic
    return render(request, 'show_result.html', {'results': results})

# --- AUTH VIEWS ---
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from accounts.forms import RegistrationForm

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful and Logged in!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Registration failed.')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')