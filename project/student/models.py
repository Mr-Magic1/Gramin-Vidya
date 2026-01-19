from django.db import models

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    clas = models.PositiveIntegerField()
    roll = models.PositiveIntegerField()

    address = models.CharField(max_length=200)
    guard = models.CharField(max_length=100)

    mobile = models.CharField(max_length=10, unique=True)

    dob = models.DateField(null=True, blank=True)

    student_img = models.ImageField(upload_to='student_faces/', null=True, blank=True)
    last_present = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
