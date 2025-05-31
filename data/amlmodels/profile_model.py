from django.db import models
from django.contrib.auth.models import User

def user_photo_path(instance, filename):
    return f"uploads/images/users/{instance.user.id}/photo/{filename}"

class Profile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
        
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    dob = models.DateField(null=True, blank=True)
    organization = models.TextField(blank=True)
    photo = models.ImageField(upload_to=user_photo_path, blank=True, null=True)
    two_fa_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user} - {self.phone}"
    
    class Meta:
        verbose_name_plural = "Profiles"
