from django.db import models

# Create your models here.
class Student(models.Model):
    name=models.CharField(max_length=100)
    clas=models.IntegerField()
    roll=models.IntegerField()
    address=models.CharField(max_length=200)
    guard=models.CharField(max_length=100)

    student_img = models.ImageField(upload_to='student_faces/', null=True, blank=True)
    # Field to track when they were last present
    last_present = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name