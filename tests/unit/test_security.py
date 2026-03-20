"""Security and RBAC tests for shipments and payments."""

import pytest
from rest_framework import status
from django.contrib.auth import get_user_model

from shipments.models import Shipment


User = get_user_model()


@pytest.mark.security
class TestAuthenticationRequirements:
    """Tests for authentication requirements on protected endpoints."""

    def test_create_shipment_unauthenticated_denied(self, api_client, test_locations):
        """Test that unauthenticated users cannot create shipments."""
        payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '5.0'
        }
        
        response = api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_initiate_payment_unauthenticated_denied(self, api_client, test_shipment):
        """Test that unauthenticated users cannot initiate payments."""
        payload = {
            'shipment_id': test_shipment.id,
            'phone': '+250799123456'
        }
        
        response = api_client.post(
            '/api/payments/initiate/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_tracking_public_access(self, api_client, test_shipment):
        """Test that tracking is publicly accessible without authentication."""
        response = api_client.get(
            f'/api/shipments/{test_shipment.tracking_code}/live/'
        )
        
        assert response.status_code == status.HTTP_200_OK

    def test_webhook_public_access(self, api_client):
        """Test that webhook is publicly accessible without authentication."""
        from django.utils import timezone
        payload = {
            'transaction_id': 'tx-test',
            'status': 'FAILURE',
            'timestamp': timezone.now().isoformat()
        }
        
        response = api_client.post(
            '/api/payments/webhook/',
            data=payload,
            format='json'
        )
        
        # Should not return 401 (permission denied for webhook as it's external)
        assert response.status_code != status.HTTP_401_UNAUTHORIZED


@pytest.mark.security
class TestUserIsolation:
    """Tests for user data isolation and permission boundaries."""

    def test_user_cannot_create_shipment_as_destination_for_another(self, db, test_locations):
        """Test that a user can only be the sender, not receiver of their own shipment."""
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='Pass123!',
            phone='+250799111111'
        )
        
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Pass123!',
            phone='+250799222222'
        )
        
        from rest_framework.test import APIClient
        api_client = APIClient()
        api_client.force_authenticate(user1)
        
        payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '5.0'
        }
        
        response = api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        # Shipment should be created with user1 as sender
        assert response.status_code == status.HTTP_201_CREATED
        shipment = Shipment.objects.get(id=response.data['id'])
        assert shipment.sender == user1

    def test_user_cannot_pay_for_another_users_shipment(self, db, test_locations):
        """Test that a user cannot initiate payment for another user's shipment."""
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='Pass123!',
            phone='+250799111111'
        )
        
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Pass123!',
            phone='+250799222222'
        )
        
        # Create shipment for user1
        shipment = Shipment.objects.create(
            tracking_code='RW-TEST001',
            sender=user1,
            origin=test_locations['origin'],
            destination=test_locations['destination'],
            tariff='10.00',
            status=Shipment.STATUS_PENDING_PAYMENT
        )
        
        # Try to pay with user2
        from rest_framework.test import APIClient
        api_client = APIClient()
        api_client.force_authenticate(user2)
        
        payload = {
            'shipment_id': shipment.id,
            'phone': '+250799222222'
        }
        
        response = api_client.post(
            '/api/payments/initiate/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_isolation_on_create_endpoint(self, db, test_locations):
        """Test that shipment sender is always the authenticated user."""
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='Pass123!',
            phone='+250799111111'
        )
        
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Pass123!',
            phone='+250799222222'
        )
        
        from rest_framework.test import APIClient
        api_client = APIClient()
        
        # Create shipment as user1
        api_client.force_authenticate(user1)
        payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '5.0'
        }
        
        response = api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        shipment_id = response.data['id']
        
        # Verify shipment belongs to user1
        shipment = Shipment.objects.get(id=shipment_id)
        assert shipment.sender == user1


@pytest.mark.security
class TestInputValidationAndSanitization:
    """Tests for input validation and prevention of injection attacks."""

    def test_create_shipment_prevents_negative_weight(self, authenticated_api_client, test_locations):
        """Test that negative weights are rejected."""
        payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '-10.0'
        }
        
        response = authenticated_api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_shipment_prevents_zero_weight(self, authenticated_api_client, test_locations):
        """Test that zero weight is rejected."""
        payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '0'
        }
        
        response = authenticated_api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_shipment_prevents_massive_weight(self, authenticated_api_client, test_locations):
        """Test that unreasonably large weights are rejected."""
        payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '999999999'
        }
        
        response = authenticated_api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_payment_phone_format_validation(self, authenticated_api_client, test_shipment):
        """Test that phone format is strictly validated."""
        invalid_phones = [
            '0788123456',  # Missing +250
            '+251799123456',  # Wrong country code
            '+250 799 123456',  # Spaces
            '+25079912345',  # Too short
            '+2507991234567',  # Too long
            '+250abc123456',  # Non-numeric
        ]
        
        for phone in invalid_phones:
            payload = {
                'shipment_id': test_shipment.id,
                'phone': phone
            }
            
            response = authenticated_api_client.post(
                '/api/payments/initiate/',
                data=payload,
                format='json'
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST, \
                f"Phone {phone} should have been rejected"

    def test_tracking_code_format_enforcement(self, api_client, db):
        """Test that tracking code is properly formatted."""
        # Try accessing with invalid tracking codes
        invalid_codes = [
            'INVALID',
            '../../../etc/passwd',
            '"; DROP TABLE shipments; --',
            '<script>alert("xss")</script>',
        ]
        
        for code in invalid_codes:
            response = api_client.get(
                f'/api/shipments/{code}/live/'
            )
            
            # All should return 404, not errors
            assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.security
class TestDataIntegrity:
    """Tests for maintaining data integrity and atomicity."""

    def test_payment_failure_does_not_corrupt_shipment(self, db, authenticated_api_client, test_locations):
        """Test that payment failure doesn't leave shipment in inconsistent state."""
        # Create shipment
        payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '5.0'
        }
        
        create_response = authenticated_api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        shipment_id = create_response.data['id']
        original_tariff = create_response.data['tariff']
        
        # Initiate payment
        payment_payload = {
            'shipment_id': shipment_id,
            'phone': '+250799123456'
        }
        
        payment_response = authenticated_api_client.post(
            '/api/payments/initiate/',
            data=payment_payload,
            format='json'
        )
        
        transaction_id = payment_response.data['transaction_id']
        
        # Simulate failure
        from django.utils import timezone
        webhook_payload = {
            'shipment_id': shipment_id,
            'transaction_id': transaction_id,
            'status': 'FAILURE',
            'timestamp': timezone.now().isoformat()
        }
        
        authenticated_api_client.post(
            '/api/payments/webhook/',
            data=webhook_payload,
            format='json'
        )
        
        # Verify shipment is in consistent state
        shipment = Shipment.objects.get(id=shipment_id)
        assert shipment.status == 'FAILED'
        assert shipment.tariff == original_tariff  # Tariff unchanged
        assert shipment.sender_id is not None  # Sender not cleared
        assert shipment.origin_id is not None  # Origin not cleared
        assert shipment.destination_id is not None  # Destination not cleared

    def test_duplicate_webhook_calls_idempotent(self, db, authenticated_api_client, test_shipment):
        """Test that calling webhook twice with same transaction doesn't cause issues."""
        from django.utils import timezone
        
        payload = {
            'shipment_id': test_shipment.id,
            'transaction_id': 'tx-duplicate-123',
            'status': 'SUCCESS',
            'timestamp': timezone.now().isoformat()
        }
        
        # First call
        response1 = authenticated_api_client.post(
            '/api/payments/webhook/',
            data=payload,
            format='json'
        )
        
        shipment_after_first = Shipment.objects.get(id=test_shipment.id)
        first_status = shipment_after_first.status
        
        # Second call with same data
        response2 = authenticated_api_client.post(
            '/api/payments/webhook/',
            data=payload,
            format='json'
        )
        
        shipment_after_second = Shipment.objects.get(id=test_shipment.id)
        second_status = shipment_after_second.status
        
        # Status should be consistent
        assert first_status == second_status
