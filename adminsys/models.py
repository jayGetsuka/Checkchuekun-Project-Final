from django.db import models

# Create your models here.
class Camera(models.Model):
    NumberRoom = models.CharField(max_length=255, unique=True)
    Link = models.CharField(max_length=255)
    statusCamera = models.BooleanField(default=False)
    
