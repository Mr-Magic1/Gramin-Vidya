import os
import face_recognition
import numpy as np
import base64
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings # Needed for file paths

# Import your models
from student.models import Student
from result.models import Result
from accounts.forms import RegistrationForm

def home(request):
    # Safe logout
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'home.html')

def student(request):
    return render(request, 'student_login.html')

def student_profile(request):
    context = {}

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Extract digits for mobile
        mobile = "".join(ch for ch in username if ch.isdigit())

        if not mobile:
            context['error'] = "Invalid username format"
            return render(request, 'student_profile.html', context)

        try:
            student = Student.objects.get(mobile=mobile)
            # Ensure safe slicing even if name is short
            first_name = student.first_name.upper() if student.first_name else ""
            
            expected_username = first_name + student.mobile
            dob_year = student.dob.year
            
            # Safe slicing for password
            name_part = first_name[:4] if len(first_name) >= 4 else first_name
            expected_password = name_part + str(dob_year)
            
            if username == expected_username and password == expected_password:
                context['student'] = student
                return render(request, 'student_profile.html', context)
            else:
                context['error'] = "Invalid username or password"

        except Student.DoesNotExist:
            context['error'] = "No student found with this mobile number"

    return render(request, 'student_profile.html', context)

def student_result(request):
    mobile = request.POST.get('mob')
    if not mobile:
        return render(request, 'student_result.html', {'error': 'Please provide a mobile number'})
        
    results = Result.objects.filter(mobile__icontains=mobile)

    for student in results:
        # Calculate totals
        student.half_total = (
            student.hmath + student.hsci + student.hhis + 
            student.heng + student.hhindi
        )

        student.final_total = (
            student.fmath + student.fsci + student.fhis + 
            student.feng + student.fhindi
        )
        student.maths_total = student.hmath + student.fmath
        student.sci_total = student.hsci + student.fsci
        student.his_total = student.hhis + student.fhis
        student.eng_total = student.heng + student.feng
        student.hindi_total = student.hhindi + student.fhindi
        
        student.grand_total = student.half_total + student.final_total
        
        grade = ''
        if student.grand_total > 850:
            grade = "A+"
        elif student.grand_total > 740:
            grade = "A"
        elif student.grand_total > 640:
            grade = "B+"
        elif student.grand_total > 500:
            grade = "B"
        elif student.grand_total > 350:
            grade = "C" # Changed lowercase c to C for consistency

        student.grade = grade

    return render(request, 'student_result.html', {'results': results})

@login_required(login_url='login')
def dashboard(request):
    today = timezone.now().date()
    total_students = Student.objects.count()
    present_count = Student.objects.filter(last_present=today).count()
    meal_count = present_count
    percentage = int((present_count / total_students) * 100) if total_students else 0

    total3=Student.objects.filter(clas=3).count()
    present3=Student.objects.filter(last_present=today,clas=3).count()
    percentage3=int((present3 / total3) * 100) if total_students else 0

    total4=Student.objects.filter(clas=4).count()
    present4=Student.objects.filter(last_present=today,clas=4).count()
    percentage4=int((present4 / total4) * 100) if total_students else 0

    total5=Student.objects.filter(clas=5).count()
    present5=Student.objects.filter(last_present=today,clas=5).count()
    percentage5=int((present5 / total5) * 100) if total_students else 0

    context = {
        'date': today,
        'total_students': total_students,
        'present_count': present_count,
        'meal_count': meal_count,
        'percentage': percentage,
        'percentage3':percentage3,
        'percentage4':percentage4,
        'percentage5':percentage5
    }
    return render(request, "dashboard.html", context)

@login_required(login_url='login')
def submit_student(request):
    reply = ""
    if request.method == "POST":
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            clas = request.POST.get("clas")
            roll = request.POST.get("roll")
            address = request.POST.get("address", "")
            guardian = request.POST.get("guard")
            mobile = request.POST.get("mobile")
            dob = request.POST.get("dob") 
            student_img = request.FILES.get("student_img")
            
            student = Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                clas=clas,
                roll=roll,
                address=address,
                guard=guardian,
                mobile=mobile,
                dob=dob,
                student_img=student_img
            )

            reply = f"Student {student.first_name} enrolled successfully!"
        except Exception as e:
            reply = f"Error enrolling student: {str(e)}"

    return render(request, "add_student.html", {"reply": reply})

@login_required(login_url='login')
def attendance(request):
    students = Student.objects.all() # Default all

    # Filter based on logged-in user (Teacher specific views)
    if request.user.username == "shrey":
        students = students.filter(clas__icontains=5)
    elif request.user.username == "Khushboo":
        students = students.filter(clas__icontains=4)
    elif request.user.username == 'Aman':
        students = students.filter(clas__icontains=3)

    if request.method == "GET":
        clas_search = request.GET.get('classsearch')
        name_search = request.GET.get('namesearch')
        
        if clas_search:              
            students = students.filter(clas__icontains=clas_search)
        if name_search:
            # Assuming you want to search by first name
            students = students.filter(first_name__icontains=name_search)
            
    student_list = []
    today = timezone.now().date()
    
    for s in students:
        status = 'absent'
        if s.last_present == today:
            status = 'present'
        
        # Construct full name safely
        full_name = f"{s.first_name} {s.last_name}"
            
        student_list.append({
            'student': s,
            'name': full_name,
            'roll': s.roll,
            'clas': s.clas,
            'status': status
        })

    return render(request, 'attendance.html', {'students': student_list})

@login_required(login_url='login')
def add_student(request):
    return render(request, 'add_student.html')


# --- Add this Global Dictionary outside the function ---
# This stores {student_id: numpy_array_of_face_encoding}
student_encodings_cache = {} 

@csrf_exempt
def scan_face_attendance(request):
    if request.method == 'POST':
        try:
            image_data = request.POST.get('image')
            if not image_data:
                return JsonResponse({'success': False, 'message': 'No image data received'})

            # 1. Decode base64 from Webcam
            try:
                format, imgstr = image_data.split(';base64,') 
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            except ValueError:
                 return JsonResponse({'success': False, 'message': 'Invalid image format'})

            # 2. Process Webcam Image (Only done once per request)
            unknown_image = face_recognition.load_image_file(data)
            unknown_encodings = face_recognition.face_encodings(unknown_image)
            
            if len(unknown_encodings) == 0:
                return JsonResponse({'success': False, 'message': 'No face detected in camera.'})
            
            unknown_encoding = unknown_encodings[0]

            # 3. Compare with DB Students (Optimized Loop)
            students = Student.objects.exclude(student_img='')
            
            for student in students:
                try:
                    # --- CACHE LOGIC START ---
                    known_encoding = None

                    # Check if we already have this student's face math in memory
                    if student.id in student_encodings_cache:
                        known_encoding = student_encodings_cache[student.id]
                    else:
                        # Only run this heavy code if NOT in cache
                        if not student.student_img or not os.path.exists(student.student_img.path):
                            continue

                        known_image = face_recognition.load_image_file(student.student_img.path)
                        known_encodings = face_recognition.face_encodings(known_image)
                        
                        if known_encodings:
                            known_encoding = known_encodings[0]
                            # Save to cache for next time!
                            student_encodings_cache[student.id] = known_encoding
                        else:
                            # If profile pic has no face, mark as None to skip next time
                            student_encodings_cache[student.id] = None
                            continue
                    
                    # If cached value is None (invalid profile pic), skip
                    if known_encoding is None:
                        continue
                    # --- CACHE LOGIC END ---
                    
                    # 4. Fast Comparison (NumPy Math)
                    # This is instant because we are comparing arrays, not processing images
                    matches = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
                    
                    if matches[0]:
                        student.last_present = timezone.now().date()
                        student.save()
                        
                        full_name = f"{student.first_name} {student.last_name}"
                        return JsonResponse({
                            'success': True, 
                            'message': f'Attendance marked for {full_name}',
                            'student_name': full_name
                        })

                except Exception as inner_e:
                    print(f"Error processing student {student.id}: {inner_e}")
                    continue

            return JsonResponse({'success': False, 'message': 'Face not recognized.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Server Error: {str(e)}"})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required(login_url='login')
def result(request):
    return render(request, 'result.html')

@login_required(login_url='login')
def update_result(request):
    reply = "Error Occurred"
    if request.method == "POST":   
        try:
            # FIX: Removed the comma after name retrieval
            name_val = request.POST.get('name') 
            
            data = Result(
                name=name_val,
                clas=request.POST.get('clas'),
                roll=request.POST.get('roll'),
                dob=request.POST.get('dob'),
                mobile=request.POST.get('mob'),
                guard=request.POST.get('guard'),
                hmath=float(request.POST.get('hmath', 0)),
                hsci=float(request.POST.get('hsci', 0)),
                hhis=float(request.POST.get('hhis', 0)),
                heng=float(request.POST.get('heng', 0)),
                hhindi=float(request.POST.get('hhindi', 0)),
                fmath=float(request.POST.get('fmath', 0)),
                fsci=float(request.POST.get('fsci', 0)),
                fhis=float(request.POST.get('fhis', 0)),
                feng=float(request.POST.get('feng', 0)),
                fhindi=float(request.POST.get('fhindi', 0)),
            )
            data.save()
            reply = f"Result of {name_val} uploaded successfully"
        except Exception as e:
            reply = f"Error saving result: {str(e)}"
            
    return render(request, 'result.html', {'reply': reply})

@login_required(login_url='login')
def show_result(request):
    results = Result.objects.all()
    
    if request.user.username == "shrey":
        results = results.filter(clas__icontains=5)
    elif request.user.username == "Khushboo":
        results = results.filter(clas__icontains=4)
    elif request.user.username == 'Aman':
        results = results.filter(clas__icontains=3)
    
    for student in results:
        student.half_total = (
            student.hmath + student.hsci + student.hhis + 
            student.heng + student.hhindi
        )

        student.final_total = (
            student.fmath + student.fsci + student.fhis + 
            student.feng + student.fhindi
        )
        student.maths_total = student.hmath + student.fmath
        student.sci_total = student.hsci + student.fsci
        student.his_total = student.hhis + student.fhis
        student.eng_total = student.heng + student.feng
        student.hindi_total = student.hhindi + student.fhindi
        
        student.grand_total = student.half_total + student.final_total
        
        grade = ''
        if student.grand_total > 850:
            grade = "A+"
        elif student.grand_total > 740:
            grade = "A"
        elif student.grand_total > 640:
            grade = "B+"
        elif student.grand_total > 500:
            grade = "B"
        elif student.grand_total > 350:
            grade = "C"

        student.grade = grade

    return render(request, 'show_result.html', {'results': results})

# Authentication Views
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
    return render(request, 'home.html')
