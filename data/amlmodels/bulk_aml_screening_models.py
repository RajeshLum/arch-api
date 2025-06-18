import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class BulkAmlScreening(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    id = models.AutoField(primary_key=True)
    reference_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bulk_aml_screenings')
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    matched_records = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    countries = models.JSONField(default=list)
    screening_models = models.JSONField(default=list)
    is_manual_review = models.BooleanField(default=False)
    decline_on_single_step = models.BooleanField(default=False)
    check_family = models.BooleanField(default=False)
    result_file_path = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bulk AML Screening {self.reference_id}"
    
    def save(self, *args, **kwargs):
        if not self.reference_id:
            self.reference_id = f"BAML-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class BulkAmlScreeningRecord(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('matched', 'Matched'),
        ('not_matched', 'Not Matched'),
        ('error', 'Error'),
    )
    
    id = models.AutoField(primary_key=True)
    bulk_screening = models.ForeignKey(BulkAmlScreening, on_delete=models.CASCADE, related_name='records')
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_id = models.IntegerField(null=True, blank=True)
    matched_entities = models.JSONField(default=list)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Record {self.id} - {self.full_name}"
