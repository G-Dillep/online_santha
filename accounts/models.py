from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    farming_experience = models.PositiveIntegerField(blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True)
    verification_document = models.FileField(upload_to='farmer_docs/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - Farmer Profile"

class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - Buyer Profile"
