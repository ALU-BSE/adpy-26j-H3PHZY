"""Unit tests for shipments.services.BookingService"""

import pytest
from decimal import Decimal
from django.utils import timezone

from shipments.services import BookingService
from shipments.models import Shipment
from core.models import Location


@pytest.mark.unit
class TestBookingService:
    """Test suite for BookingService business logic."""

    @pytest.fixture
    def service(self):
        return BookingService()

    @pytest.fixture
    def test_locations(self, db):
        same_zone_loc = Location.objects.create(
            name='Location A',
            location_type='SECTOR',
            code='LOC-001'
        )
        different_zone_loc = Location.objects.create(
            name='Location B',
            location_type='SECTOR',
            code='LOC-002'
        )
        return {
            'same_zone': same_zone_loc,
            'different_zone': different_zone_loc
        }

    def test_generate_tracking_code(self, service):
        code1 = service._generate_tracking_code()
        code2 = service._generate_tracking_code()
        
        assert code1.startswith('RW-')
        assert len(code1) == 11
        assert code1 != code2
        assert code1.replace('RW-', '').isalnum()

    def test_calculate_tariff_same_zone(self, service, test_locations):
        tariff = service.calculate_tariff(
            origin=test_locations['same_zone'],
            destination=test_locations['same_zone'],
            weight_kg=Decimal('10.0')
        )
        assert tariff == Decimal('25.00')

    def test_calculate_tariff_different_zone(self, service, test_locations):
        tariff = service.calculate_tariff(
            origin=test_locations['same_zone'],
            destination=test_locations['different_zone'],
            weight_kg=Decimal('5.5')
        )
        assert tariff == Decimal('21.00')

    def test_calculate_tariff_decimal_precision(self, service, test_locations):
        tariff = service.calculate_tariff(
            origin=test_locations['same_zone'],
            destination=test_locations['same_zone'],
            weight_kg=Decimal('3.75')
        )
        assert tariff == Decimal('12.50')
        assert isinstance(tariff, Decimal)

    def test_create_shipment_sets_pending_payment_status(self, db, service, authenticated_user, test_locations):
        """Test that created shipment starts in PENDING_PAYMENT status."""
        shipment = service.create_shipment(
            sender=authenticated_user,
            origin=test_locations['same_zone'],
            destination=test_locations['different_zone'],
            weight_kg=Decimal('10.0'),
            description='Test shipment'
        )
        
        assert shipment.status == Shipment.STATUS_PENDING_PAYMENT
        assert shipment.sender == authenticated_user
        assert shipment.tracking_code is not None
        assert shipment.tariff is not None

    def test_confirm_payment_success(self, db, service, test_shipment):
        """Test confirm_payment marks shipment as PAID on success."""
        result = service.confirm_payment(test_shipment, success=True)
        
        assert result.status == Shipment.STATUS_PAID
        # Refresh from DB to confirm persistence
        test_shipment.refresh_from_db()
        assert test_shipment.status == Shipment.STATUS_PAID

    def test_confirm_payment_failure_clears_driver(self, db, service, test_shipment, authenticated_user):
        """Test confirm_payment clears driver and marks FAILED on failure."""
        # Assign a driver first
        test_shipment.driver = authenticated_user
        test_shipment.save()
        
        # Confirm payment failure
        result = service.confirm_payment(test_shipment, success=False)
        
        assert result.status == Shipment.STATUS_FAILED
        assert result.driver is None
        # Verify in database
        test_shipment.refresh_from_db()
        assert test_shipment.status == Shipment.STATUS_FAILED
        assert test_shipment.driver is None

    def test_assign_driver(self, db, service, test_shipment, authenticated_user):
        """Test assign_driver marks shipment as DISPATCHED."""
        # Shipment must be PAID before dispatch
        test_shipment.status = Shipment.STATUS_PAID
        test_shipment.save()
        
        result = service.assign_driver(test_shipment, authenticated_user)
        
        assert result.status == Shipment.STATUS_DISPATCHED
        assert result.driver == authenticated_user
        # Verify in database
        test_shipment.refresh_from_db()
        assert test_shipment.status == Shipment.STATUS_DISPATCHED
        assert test_shipment.driver == authenticated_user

    def test_atomic_transaction_create_shipment(self, db, service, authenticated_user, test_locations):
        """Test that create_shipment is atomic."""
        initial_count = Shipment.objects.count()
        
        shipment = service.create_shipment(
            sender=authenticated_user,
            origin=test_locations['same_zone'],
            destination=test_locations['different_zone'],
            weight_kg=Decimal('5.0'),
            description='Atomic test'
        )
        
        assert Shipment.objects.count() == initial_count + 1
        assert shipment.id is not None  # Persisted to DB
