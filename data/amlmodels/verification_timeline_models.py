from django.db import models
from django.contrib.auth.models import User
from data.amlmodels.verification_models import Verification

class VerificationTimeline(models.Model):
    """
    Model to track the history of verification status changes.
    """
    verification = models.ForeignKey(
        Verification, 
        on_delete=models.CASCADE, 
        related_name="timeline_entries"
    )
    status = models.CharField(max_length=20, blank=True, null=True)
    action = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    performed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="verification_actions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Timeline entry for Verification {self.verification.id}: {self.action}"

    class Meta:
        verbose_name = "Verification Timeline"
        verbose_name_plural = "Verification Timelines"
        ordering = ['-created_at']
