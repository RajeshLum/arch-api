from django.db import models
from data.amlmodels.verification_models import Verification

class VerificationMetadata(models.Model):
    """
    Model to store metadata about verification requests including IP and browser information.
    """
    verification = models.OneToOneField(
        Verification, 
        on_delete=models.CASCADE, 
        related_name="metadata"
    )
    ip_address = models.CharField(max_length=45, blank=True, null=True)  # IPv6 can be up to 45 chars
    user_agent = models.TextField(blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)
    browser_version = models.CharField(max_length=50, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    device = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Metadata for Verification {self.verification.id}"

    class Meta:
        verbose_name = "Verification Metadata"
        verbose_name_plural = "Verification Metadata"
