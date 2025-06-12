from django.db import models
from django.contrib.auth.models import User

class CustomStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="custom_statuses")
    label = models.CharField(max_length=100)
    value = models.CharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.status_name}"

    class Meta:
        db_table = "custom_statuses"
        verbose_name_plural = "Custom Statuses"
