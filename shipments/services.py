from decimal import Decimal
from django.db import transaction
from django.utils.crypto import get_random_string

from .models import Shipment
from core.models import Location, User


class BookingService:
    """Service layer for handling shipment bookings, tariffs, payments, and driver assignments."""

    @staticmethod
    def _generate_tracking_code() -> str:
        return f"RW-{get_random_string(8, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')}"

    def calculate_tariff(self, origin: Location, destination: Location, weight_kg: Decimal) -> Decimal:
        """Calculate tariff based on origin/destination and weight."""
        base = Decimal('5.00') if origin.id == destination.id else Decimal('10.00')
        return base + (Decimal('2.00') * weight_kg)

    @transaction.atomic
    def create_shipment(self, sender: User, origin: Location, destination: Location, weight_kg: Decimal, description: str) -> Shipment:
        """
        Create a shipment record with a unified workflow.
        Steps: Calculate Tariff -> Generate Code -> Create Record (Atomic).
        """
        tariff = self.calculate_tariff(origin, destination, weight_kg)
        tracking = self._generate_tracking_code()
        
        shipment = Shipment.objects.create(
            tracking_code=tracking,
            sender=sender,
            origin=origin,
            destination=destination,
            tariff=tariff,
            description=description,
            status=Shipment.STATUS_PENDING_PAYMENT,
        )
        return shipment

    @transaction.atomic
    def confirm_payment(self, shipment: Shipment, success: bool) -> Shipment:
        """
        Mark shipment as PAID or FAILED and trigger follow-up transitions.
        Atomic to ensure status consistency across payment gates and notifications.
        """
        if success:
            shipment.status = Shipment.STATUS_PAID
            # In a real integration, this would trigger RURA driver matching
        else:
            shipment.status = Shipment.STATUS_FAILED
            shipment.driver = None
            
        shipment.save()
        return shipment

    @transaction.atomic
    def assign_driver(self, shipment: Shipment, driver: User) -> Shipment:
        """Assign driver and mark shipment as dispatched."""
        shipment.driver = driver
        shipment.status = Shipment.STATUS_DISPATCHED
        shipment.save()
        return shipment
