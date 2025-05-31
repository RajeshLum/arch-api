from django.db import models
from django.contrib.auth.models import User

class FlagApproval(models.Model):
    REASON_TYPES = (
        ('suspicious_activity', 'Suspicious Activity'),
        ('unusual_transaction', 'Unusual Transaction'),
        ('high_risk_country', 'High Risk Country'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="flag_approvals")
    verification_id = models.CharField(max_length=20, blank=True, null=True)
    customer_id = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True)
    reason_type = models.CharField(max_length=20, choices=REASON_TYPES, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    forwarded_to = models.CharField(max_length=20, blank=True, null=True)
    forward_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = "flag_approvals"
        verbose_name_plural = "Flag & Approval"
        
