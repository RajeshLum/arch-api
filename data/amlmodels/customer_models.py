import uuid
import os

from django.db import models
from django.contrib.auth.models import User

def customer_photo_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    return f"uploads/images/customers/photo/{filename}"
  
def customer_document_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    return f"uploads/documents/customers/{instance.customer.id}/{filename}"

class Customer(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customers")
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=50, blank=True, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    nationality = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    tax_id = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to=customer_photo_path, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    is_flagged = models.BooleanField(default=False)
    success_attempts = models.IntegerField(default=0)
    failed_attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.email} - {self.phone}"

    class Meta:
        db_table = "customers"
        verbose_name_plural = "Customers"
        
class Identity(models.Model):
    ID_TYPES = (
        ('passport', 'Passport'),
        ('driving_license', "Driver's License"),
        ('nid', 'National ID'),
    )
    
    COUNTRIES = (
        ('bd', 'Bangladesh'),
        ('usa', "United States of America"),
    )
        
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="identities")
    id_type = models.CharField(max_length=20, choices=ID_TYPES, blank=True, null=True)
    id_number = models.CharField(max_length=20, blank=True, null=True)
    issuing_country = models.CharField(max_length=20, choices=COUNTRIES, blank=True, null=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    document = models.FileField(upload_to=customer_document_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id_number}"

    class Meta:
        db_table = "identities"
        verbose_name_plural = "Identities"

class Employability(models.Model):
    EMPLOYMENT_STATUS = (
        ('employed', 'Employed'),
        ('self_employed', "Self-Employed"),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="employabilities")
    status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    employer_name = models.CharField(max_length=50, blank=True, null=True)
    employer_address = models.CharField(max_length=50, blank=True, null=True)
    annual_income = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = "employabilities"
        verbose_name_plural = "Employability"

class BankInfo(models.Model):
    ACCOUNT_TYPE = (
        ('savings', 'Savings'),
        ('checking', 'Checking'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="bank_info")
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE, blank=True, null=True)
    swift_code_iban = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = "bank_info"
        verbose_name_plural = "Bank Information"
        
class CustomerAdditionalInfo(models.Model):
    PEP_STATUS = (
        ('yes', 'Yes'),
        ('no', 'No'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_addi_info")
    account_purpose = models.CharField(max_length=255, blank=True, null=True)
    expected_transactions = models.CharField(max_length=20, blank=True, null=True)
    annual_turnover = models.CharField(max_length=50, blank=True, null=True)
    fund_source = models.CharField(max_length=255, blank=True, null=True)
    pep_status = models.CharField(max_length=20, choices=PEP_STATUS, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        
        return f"{self.id}"

    class Meta:
        db_table = "customer_addi_info"
        verbose_name_plural = "Customer Additional Information"
        
class BusinessInfo(models.Model):
    BUSINESS_TYPE = (
        ('corporation', 'Corporation'),
    )
    
    COUNTRIES = (
        ('bd', 'Bangladesh'),
        ('usa', "United States of America"),
    )
    
    INDUSTRY_SECTOR = (
        ('it', 'Information Technology'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="business_info")
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    regi_number = models.CharField(max_length=50, blank=True, null=True)
    incorporation_date = models.DateField(null=True, blank=True)
    incorporation_country = models.CharField(max_length=20, choices=COUNTRIES, blank=True, null=True)
    registered_address = models.CharField(max_length=255, blank=True, null=True)
    operational_address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=50, blank=True, unique=True)
    website = models.CharField(max_length=50, blank=True, null=True)
    industry_sector = models.CharField(max_length=50, choices=INDUSTRY_SECTOR, blank=True, null=True)
    key_products_services = models.CharField(max_length=255, blank=True, null=True)
    business_activities_desc = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = "business_info"
        verbose_name_plural = "Business Information"
        