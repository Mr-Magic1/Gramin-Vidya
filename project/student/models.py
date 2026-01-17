from django.db import models

# Create your models here.
class Student(models.Model):
    name=models.CharField(max_length=100)
    clas=models.IntegerField()
    roll=models.IntegerField()
    address=models.CharField(max_length=200)
    guard=models.CharField(max_length=100)

    def __str__(self):
        return self.name