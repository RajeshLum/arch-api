import uuid
import os

from django.db import models
from django.contrib.auth.models import User

class Verification(models.Model):
    ID_TYPES = (
        ('passport', 'Passport'),
        ('driving_license', "Driver's License"),
        ('nid', 'National ID'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verifications")
    customer_id = models.CharField(max_length=20, blank=True, null=True)
    id_type = models.CharField(max_length=20, choices=ID_TYPES, blank=True, null=True)
    document = models.JSONField(default=list)
    service_id = models.IntegerField(default=0)
    status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id} - {self.customer_id}"

    class Meta:
        db_table = "verifications"
        verbose_name_plural = "Verifications"
        
