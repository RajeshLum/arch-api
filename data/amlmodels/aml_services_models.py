from django.db import models
from django.contrib.auth.models import User

class AmlService(models.Model):
    """
    Model for AML services tracking different types of verification services.
    """
    SERVICE_CATEGORIES = (
        ('aml', 'AML Screening'),
        ('idv', 'Identity Verification'),
        ('kyb', 'Know Your Business'),
        ('investor_verification', 'Investor Verification'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="aml_services")
    service_name = models.CharField(max_length=100)
    service_category = models.CharField(max_length=30, choices=SERVICE_CATEGORIES)
    status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id} - {self.service_name}"

    class Meta:
        db_table = "aml_services"
        verbose_name_plural = "AML Services"
