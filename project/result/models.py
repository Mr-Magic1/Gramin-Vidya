from django.db import models

# Create your models here.
class Result(models.Model):
    name = models.CharField(max_length=100)
    clas = models.IntegerField()
    roll = models.IntegerField(unique=True)
    guard = models.CharField(max_length=100) 
    mobile = models.CharField(max_length=10)
    dob = models.DateField(null=True, blank=True)

    hmath = models.IntegerField()
    hsci = models.IntegerField()
    hhis = models.IntegerField()
    heng = models.IntegerField()
    hhindi = models.IntegerField()

    fmath = models.IntegerField()
    fsci = models.IntegerField()
    fhis = models.IntegerField()
    feng = models.IntegerField()
    fhindi = models.IntegerField()

    def __str__(self):
        return self.name
    
    