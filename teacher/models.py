from django.db import models
from django.contrib.auth.models import User
from adminsys.models import Camera

# Create your models here.
class Teacher(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    firstname = models.CharField(max_length=50) 
    lastname = models.CharField(max_length=50)
    department = models.CharField(max_length=255, null=True, blank=True)
    phone_no = models.CharField(max_length=10, null=True, blank=True)

class Subject(models.Model):
    SubjectCode = models.CharField(max_length=50, unique=True)
    SubjectName = models.CharField(max_length=255)
    SubjectRoom = models.ForeignKey(Camera, on_delete=models.CASCADE)
    Teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

class ClassMember(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class AttendanceHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    time = models.TimeField()
    image = models.FilePathField(null=True)