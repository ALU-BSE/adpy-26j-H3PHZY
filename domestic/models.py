from django.db import models
from django.contrib.auth import get_user_model
from core.models import Location
from decimal import Decimal

User = get_user_model()


class Shipment(models.Model):
    """Base shipment model with common fields"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_TRANSIT', 'In Transit'),
        ('ARRIVED_HUB', 'Arrived at Hub'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    
    tracking_number = models.CharField(max_length=20, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_shipments')
    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(max_length=13)
    
    origin_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='origin_shipments')
    destination_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='destination_shipments')
    
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['status']),
            models.Index(fields=['sender']),
        ]
    
    def __str__(self):
        return f"{self.tracking_number} - {self.status}"


class ShipmentLog(models.Model):
    """Track shipment movements and status changes"""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    logged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['shipment', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status} at {self.timestamp}"
