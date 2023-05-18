from django.db import models
from django.contrib.auth.models import User
import pickle

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_no = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    image = models.ImageField(upload_to="profile/", null=True, blank=True)
    folder_image = models.FilePathField()

class Encode(models.Model):
    face_name = models.CharField(max_length=100)
    face_encode = models.BinaryField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def set_data(self, ndarray):
        self.face_encode = pickle.dumps(ndarray)
        
    def get_data(self):
        return pickle.loads(self.face_encode)