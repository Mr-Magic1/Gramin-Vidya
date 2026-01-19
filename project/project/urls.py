"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from project import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('attendance/',views.attendance,name='attendance'),
    path('add_student',views.add_student,name='add_student'),
    path('submitstudent/',views.submit_student,name='submitstudent'),
    path('result/',views.result,name='result'),
    path('update_result/',views.update_result,name='update_result'),
    path('show_result/',views.show_result,name='show_result'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('ajax/scan_face/', views.scan_face_attendance, name='scan_face_attendance'),

    path('student/',views.student,name='student'),

    path('student_profile',views.student_profile,name='student_profile'),
    path('student_result',views.student_result,name='student_result')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)