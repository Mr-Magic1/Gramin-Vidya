from django.shortcuts import render,redirect
from django.http import HttpResponse
from student.models import Student
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def home(request):
    return render(request,'dashboard.html')

@login_required(login_url='login')
def dashboard(request):
    return render(request,"dashboard.html")

@login_required(login_url='login')
def submit_student(request):
    reply="Error Occured"
    if request.method=="POST":
        name=request.POST.get('name')
        clas=request.POST.get('class')
        roll=request.POST.get('rollNo')
        address=request.POST.get('address')
        guardian=request.POST.get('guardian')
        data=Student(name=name,clas=clas,roll=roll,address=address,guard=guardian)
        data.save()
        reply="Data uploaded successfully"
    return render(request,'add_student.html',{'reply':reply})

@login_required(login_url='login')
def attendance(request):
    if request.user.username=="shrey":
        students=Student.objects.filter(clas__icontains=5)
    if request.user.username=="Khushboo":
        students=Student.objects.filter(clas__icontains=4)
    if request.method=="GET":
        clas=request.GET.get('classsearch')
        name=request.GET.get('namesearch')
        if clas!=None:               
            students=Student.objects.filter(clas__icontains=clas)
        if name!=None:
            students=Student.objects.filter(name__icontains=name)
    return render(request, 'attendance.html',{'students':students})


# to update the result of the students
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

from result.models import Result
from result.models import Result

@login_required(login_url='login')
def show_result(request):
    results = Result.objects.all()

    for student in results:
        student.half_total = (
            student.hmath +
            student.hsci +
            student.hhis +
            student.heng +
            student.hhindi
        )

        student.final_total = (
            student.fmath +
            student.fsci +
            student.fhis +
            student.feng +
            student.fhindi
        )
        student.maths_total=(
            student.hmath+student.fmath
        )
        student.sci_total=(
            student.hsci+student.fsci
        )
        student.his_total=(
            student.hhis+student.fhis
        )
        student.eng_total=(
            student.heng+student.feng
        )
        student.hindi_total=(
            student.hhindi+student.fhindi
        )
        grade=''
        student.grand_total = student.half_total + student.final_total
        if (student.grand_total>850):
            grade="A+"
        elif(student.grand_total>740):
            grade="A"
        elif (student.grand_total>640):
            grade="B+"
        elif (student.grand_total>500):
            grade="B"
        elif (student.grand_total>350):
            grade="c"

        student.grade=grade

    return render(request, 'show_result.html', {'results': results})


@login_required(login_url='login')
def add_student(request):
    return render(request,'add_student.html')



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
            messages.error(request, 'Registration failed. Please correct the errors below.')
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

