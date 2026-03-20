from django.db import models
from django.contrib.auth import get_user_model

from core.models import Location

User = get_user_model()


class Shipment(models.Model):
    """Generic shipment used by unified booking flow"""
    STATUS_PENDING_PAYMENT = 'PENDING_PAYMENT'
    STATUS_PAID = 'PAID'
    STATUS_DISPATCHED = 'DISPATCHED'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = (
        (STATUS_PENDING_PAYMENT, 'Pending payment'),
        (STATUS_PAID, 'Paid'),
        (STATUS_DISPATCHED, 'Dispatched'),
        (STATUS_FAILED, 'Failed'),
    )

    tracking_code = models.CharField(max_length=30, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipments')
    origin = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='shipments_origin')
    destination = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='shipments_destination')
    tariff = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING_PAYMENT)
    # in absence of a dedicated Driver model, reuse User (agents/drivers)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_shipments')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_code']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.tracking_code} - {self.status}"
