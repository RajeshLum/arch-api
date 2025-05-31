from django.db import models
from django.contrib.auth.models import User

class ResearchRequest(models.Model):
    PRIORITY_TYPES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    RESEARCH_TYPES = (
        ('external_data_source', 'External Data Source'),
        ('transaction_analysis', 'Transaction Analysis'),
        ('customer_profile', 'Customer Profile'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="research_requests")
    customer_id = models.CharField(max_length=20, blank=True, null=True)
    document = models.JSONField(default=list)
    status = models.CharField(max_length=50, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_TYPES, blank=True, null=True)
    research_type = models.CharField(max_length=20, choices=RESEARCH_TYPES, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = "research_requests"
        verbose_name_plural = "Research Request"
        
