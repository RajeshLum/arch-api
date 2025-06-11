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
    description = models.TextField(blank=True)  # Now optional
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=10, blank=True)  # New: country code (e.g. 'US')
    city = models.CharField(max_length=64, blank=True)     # Optional: city
    browser = models.CharField(max_length=64, blank=True)  # New: browser name
    browser_version = models.CharField(max_length=32, blank=True)  # New: browser version
    os = models.CharField(max_length=64, blank=True)       # New: operating system
    device = models.CharField(max_length=64, blank=True)   # New: device type
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SUCCESS')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "activity_logs"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return f"{self.created_at} - {self.activity} - {self.user}"
