from django.db import models
from django.contrib.auth.models import User

class ActivityLogs(models.Model):
    ACTIVITY_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('SEARCH', 'Search'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='OTHER')
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SUCCESS')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "activity_logs"
        verbose_name_plural = "Activity Logs"
         
    def __str__(self):
        return f"{self.created_at} - {self.activity} - {self.user}"
