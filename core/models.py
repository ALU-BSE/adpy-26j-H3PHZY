from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from .fields import EncryptedTextField

class User(AbstractUser):
    """Custom user model with Rwanda context"""
    USER_TYPE_CHOICES = (
        ('AGENT', 'Agent'),
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='CUSTOMER')
    phone = models.CharField(
        max_length=13,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+2507\d{8}$',
                message='Phone must be in format +250 7XX XXX XXX',
                code='invalid_phone'
            )
        ]
    )
    # Store NID encrypted at rest. Value is decrypted when accessed.
    national_id = EncryptedTextField(
        unique=True,
        blank=True,
        null=True,
        help_text='Encrypted Rwanda National ID (16 digits)'
    )
    assigned_sector = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['user_type']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"


class Location(models.Model):
    """Rwanda locations - Districts and Sectors"""
    LOCATION_TYPE_CHOICES = (
        ('DISTRICT', 'District'),
        ('SECTOR', 'Sector'),
    )
    
    name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPE_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    code = models.CharField(max_length=10, unique=True)
    
    class Meta:
        unique_together = ('name', 'parent')
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.name} ({self.parent.name})"
        return self.name
