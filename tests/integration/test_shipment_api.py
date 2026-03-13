"""Integration tests for shipments API endpoints."""

import pytest
from decimal import Decimal
from rest_framework import status

from shipments.models import Shipment


@pytest.mark.integration
class TestShipmentCreateEndpoint:
    """Integration tests for shipment creation endpoint."""

    def test_create_shipment_success(self, authenticated_api_client, test_locations):
        """Test successful shipment creation."""
        payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '5.5',
            'description': 'Test shipment'
        }
        
        response = authenticated_api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        # Debug output
        if response.status_code not in [status.HTTP_201_CREATED, status.HTTP_200_OK]:
            print(f"Response status: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"Response data: {response.data}")
            else:
                print(f"Response content: {response.content}")
        
        assert response.status_code == status.HTTP_201_CREATED, f"Got {response.status_code}: {response.data if hasattr(response, 'data') else response.content}"
        assert 'tracking_code' in response.data
        assert response.data['status'] == 'PENDING_PAYMENT'
        assert response.data['tariff'] is not None
        assert float(response.data['tariff']) > 0

    def test_create_shipment_missing_origin(self, authenticated_api_client, test_locations):
        """Test shipment creation fails without origin."""
        payload = {
            'destination_id': test_locations['destination'].id,
            'weight_kg': '5.5'
        }
        
        response = authenticated_api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_shipment_invalid_location(self, authenticated_api_client, test_locations):
        """Test shipment creation fails with invalid location ID."""
        payload = {
            'origin_id': 99999,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '5.5'
        }
        
        response = authenticated_api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Location not found' in response.data['error']

    def test_create_shipment_negative_weight(self, authenticated_api_client, test_locations):
        """Test shipment creation fails with negative weight."""
        payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '-5.5'
        }
        
        response = authenticated_api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Error could be in 'error' or 'weight_kg' field
        assert 'weight_kg' in response.data or 'error' in response.data or any(
            'greater than 0' in str(v).lower() for v in response.data.values()
        )

    def test_create_shipment_requires_authentication(self, api_client, test_locations):
        """Test shipment creation requires authentication."""
        payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '5.5'
        }
        
        response = api_client.post(
            '/api/shipments/create/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestTrackingLiveEndpoint:
    """Integration tests for live tracking endpoint."""

    def test_tracking_live_success(self, api_client, test_shipment):
        """Test successful tracking retrieval."""
        response = api_client.get(
            f'/api/shipments/{test_shipment.tracking_code}/live/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['tracking_code'] == test_shipment.tracking_code
        assert 'current_location' in response.data
        assert 'latitude' in response.data['current_location']
        assert 'longitude' in response.data['current_location']
        assert response.data['status'] == test_shipment.status

    def test_tracking_live_nonexistent_shipment(self, db, api_client):
        """Test tracking nonexistent shipment returns 404."""
        response = api_client.get(
            '/api/shipments/RW-NOTEXIST/live/'
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # Error message might be in 'error' field or 'detail' field
        assert 'error' in response.data or 'detail' in response.data or 'not found' in str(response.data).lower()

    def test_tracking_live_public_access(self, api_client, test_shipment):
        """Test tracking is publicly accessible (no authentication required)."""
        response = api_client.get(
            f'/api/shipments/{test_shipment.tracking_code}/live/'
        )
        
        assert response.status_code == status.HTTP_200_OK

    def test_tracking_live_includes_destination(self, api_client, test_shipment, test_locations):
        """Test tracking response includes destination name."""
        response = api_client.get(
            f'/api/shipments/{test_shipment.tracking_code}/live/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['destination'] == test_locations['destination'].name


@pytest.mark.integration
class TestPaymentInitiateEndpoint:
    """Integration tests for payment initiation endpoint."""

    def test_initiate_payment_success(self, authenticated_api_client, test_shipment):
        """Test successful payment initiation."""
        payload = {
            'shipment_id': test_shipment.id,
            'phone': '+250799123456'
        }
        
        response = authenticated_api_client.post(
            '/api/payments/initiate/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'transaction_id' in response.data
        assert response.data['shipment_id'] == test_shipment.id
        assert response.data['status'] == 'INITIATED'
        assert float(response.data['amount']) == float(test_shipment.tariff)

    def test_initiate_payment_requires_pending_status(self, authenticated_api_client, test_shipment):
        """Test payment initiation only works for PENDING_PAYMENT shipments."""
        # Mark shipment as already paid
        test_shipment.status = 'PAID'
        test_shipment.save()
        
        payload = {
            'shipment_id': test_shipment.id,
            'phone': '+250799123456'
        }
        
        response = authenticated_api_client.post(
            '/api/payments/initiate/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cannot initiate payment' in response.data['error']

    def test_initiate_payment_invalid_phone(self, authenticated_api_client, test_shipment):
        """Test payment initiation fails with invalid phone format."""
        payload = {
            'shipment_id': test_shipment.id,
            'phone': '0788123456'  # Missing +250
        }
        
        response = authenticated_api_client.post(
            '/api/payments/initiate/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Error could be in 'phone' field or 'error' field
        assert 'phone' in response.data or 'error' in response.data or 'valid' in str(response.data).lower()

    def test_initiate_payment_requires_authentication(self, api_client, test_shipment):
        """Test payment initiation requires authentication."""
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

    def test_initiate_payment_permission_denied(self, api_client, authenticated_user, test_shipment):
        """Test user cannot initiate payment for another user's shipment."""
        # Create a different user and authenticate with them
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='OtherPass123!',
            phone='+250799654321'
        )
        
        # Authenticate with other user
        api_client.force_authenticate(other_user)
        
        payload = {
            'shipment_id': test_shipment.id,
            'phone': '+250799123456'
        }
        
        response = api_client.post(
            '/api/payments/initiate/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'permission' in response.data['error'].lower()
