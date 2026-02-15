from django.db import models
from django.contrib.auth import get_user_model
from core.models import Location
from decimal import Decimal

User = get_user_model()


class InternationalShipment(models.Model):
    """International shipment with customs documentation"""
    DESTINATION_CHOICES = (
        ('KAMPALA', 'Kampala, Uganda'),
        ('NAIROBI', 'Nairobi, Kenya'),
        ('GOMA', 'Goma, DRC'),
        ('BUJUMBURA', 'Bujumbura, Burundi'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CLEARED_CUSTOMS_RW', 'Cleared Rwanda Customs'),
        ('IN_TRANSIT', 'In Transit'),
        ('ARRIVED_DESTINATION', 'Arrived at Destination'),
        ('CLEARED_CUSTOMS_DEST', 'Cleared Destination Customs'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    
    tracking_number = models.CharField(max_length=20, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='intl_shipments')
    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(max_length=13)
    
    origin_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='intl_origin_shipments')
    destination = models.CharField(max_length=20, choices=DESTINATION_CHOICES)
    
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    # Customs documentation (store TINs encrypted at rest)
    from core.fields import EncryptedTextField

    sender_tin = EncryptedTextField(help_text="Rwanda TIN for sender")
    recipient_passport = models.CharField(max_length=20, blank=True)
    recipient_tin = EncryptedTextField(blank=True)
    
    hs_code = models.CharField(max_length=20, blank=True, help_text="Harmonized System Code")
    customs_value = models.DecimalField(max_digits=12, decimal_places=2)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['destination', 'status']),
        ]
    
    def __str__(self):
        return f"{self.tracking_number} to {self.destination} - {self.status}"


class CustomsDocument(models.Model):
    """Customs documentation for international shipments"""
    intl_shipment = models.OneToOneField(InternationalShipment, on_delete=models.CASCADE, related_name='customs_doc')
    
    declaration_number = models.CharField(max_length=30, unique=True)
    declared_value = models.DecimalField(max_digits=12, decimal_places=2)
    origin_country = models.CharField(max_length=2, default='RW')
    destination_country = models.CharField(max_length=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Customs Doc {self.declaration_number}"
