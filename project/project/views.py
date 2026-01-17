from django.shortcuts import render
from django.http import HttpResponse
from student.models import Student
def home(request):
    return render(request,'dashboard.html')

def dashboard(request):
    return render(request,"dashboard.html")

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

def attendance(request):
    students=Student.objects.all()
    if request.method=="GET":
        clas=request.GET.get('classsearch')
        name=request.GET.get('namesearch')
        if clas!=None:               
            students=Student.objects.filter(clas__icontains=clas)
        if name!=None:
            students=Student.objects.filter(name__icontains=name)
    return render(request, 'attendance.html',{'students':students})


# to update the result of the students
def result(request):
    return render(request,'result.html')


from result.models import Result 
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



def add_student(request):
    return render(request,'add_student.html')

