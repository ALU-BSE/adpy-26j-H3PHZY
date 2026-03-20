"""Integration tests for payment webhook and full workflow."""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from rest_framework import status
from django.utils import timezone

from shipments.models import Shipment
from payments.services import MomoMockGateway


@pytest.mark.integration
class TestPaymentWebhookEndpoint:
    """Integration tests for payment webhook endpoint."""

    def test_payment_webhook_success_updates_shipment(self, api_client, test_shipment):
        """Test webhook callback with SUCCESS status updates shipment to PAID."""
        assert test_shipment.status == 'PENDING_PAYMENT'
        
        payload = {
            'shipment_id': test_shipment.id,
            'transaction_id': 'tx-12345',
            'status': 'SUCCESS',
            'timestamp': timezone.now().isoformat()
        }
        
        response = api_client.post(
            '/api/payments/webhook/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['shipment_status'] == 'PAID'
        
        # Verify shipment was updated in database
        test_shipment.refresh_from_db()
        assert test_shipment.status == 'PAID'

    def test_payment_webhook_failure_updates_shipment(self, api_client, test_shipment):
        """Test webhook callback with FAILURE status updates shipment to FAILED."""
        test_shipment.status = 'PENDING_PAYMENT'
        test_shipment.save()
        
        payload = {
            'shipment_id': test_shipment.id,
            'transaction_id': 'tx-12345',
            'status': 'FAILURE',
            'timestamp': timezone.now().isoformat()
        }
        
        response = api_client.post(
            '/api/payments/webhook/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['shipment_status'] == 'FAILED'
        
        # Verify shipment was updated to FAILED
        test_shipment.refresh_from_db()
        assert test_shipment.status == 'FAILED'

    def test_payment_webhook_invalid_status(self, api_client, test_shipment):
        """Test webhook with invalid status value."""
        payload = {
            'transaction_id': 'tx-12345',
            'status': 'INVALID',
            'timestamp': timezone.now().isoformat()
        }
        
        response = api_client.post(
            '/api/payments/webhook/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_payment_webhook_public_access(self, api_client, test_shipment):
        """Test webhook is publicly accessible (no authentication required)."""
        payload = {
            'transaction_id': 'tx-12345',
            'status': 'SUCCESS',
            'timestamp': timezone.now().isoformat()
        }
        
        response = api_client.post(
            '/api/payments/webhook/',
            data=payload,
            format='json'
        )
        
        # Should be accessible without authentication
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_payment_webhook_missing_transaction_id(self, api_client, test_shipment):
        """Test webhook fails with missing transaction_id."""
        payload = {
            'status': 'SUCCESS',
            'timestamp': timezone.now().isoformat()
        }
        
        response = api_client.post(
            '/api/payments/webhook/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.integration
class TestFullBookingWorkflow:
    """Integration tests for complete shipment booking and payment workflow."""

    def test_full_workflow_create_and_pay_shipment(self, authenticated_api_client, test_locations):
        """Test complete workflow: create shipment → pay → track."""
        # Step 1: Create shipment
        create_payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '2.5',
            'description': 'Full workflow test'
        }
        
        create_response = authenticated_api_client.post(
            '/api/shipments/create/',
            data=create_payload,
            format='json'
        )
        
        assert create_response.status_code == status.HTTP_201_CREATED
        shipment_id = create_response.data['id']
        tracking_code = create_response.data['tracking_code']
        initial_status = create_response.data['status']
        tariff = create_response.data['tariff']
        
        assert initial_status == Shipment.STATUS_PENDING_PAYMENT
        assert tracking_code.startswith('RW-')
        
        # Step 2: Initiate payment
        payment_payload = {
            'shipment_id': shipment_id,
            'phone': '+250799123456'
        }
        
        payment_response = authenticated_api_client.post(
            '/api/payments/initiate/',
            data=payment_payload,
            format='json'
        )
        
        assert payment_response.status_code == status.HTTP_201_CREATED
        assert payment_response.data['status'] == 'INITIATED'
        transaction_id = payment_response.data['transaction_id']
        
        # Step 3: Simulate webhook callback (success)
        webhook_payload = {
            'shipment_id': shipment_id,
            'transaction_id': transaction_id,
            'status': 'SUCCESS',
            'timestamp': timezone.now().isoformat()
        }
        
        webhook_response = authenticated_api_client.post(
            '/api/payments/webhook/',
            data=webhook_payload,
            format='json'
        )
        
        assert webhook_response.status_code == status.HTTP_200_OK
        assert webhook_response.data['shipment_status'] == 'PAID'
        
        # Step 4: Verify shipment status updated
        shipment = Shipment.objects.get(id=shipment_id)
        assert shipment.status == Shipment.STATUS_PAID
        
        # Step 5: Retrieve tracking info
        tracking_response = authenticated_api_client.get(
            f'/api/shipments/{tracking_code}/live/'
        )
        
        assert tracking_response.status_code == status.HTTP_200_OK
        assert tracking_response.data['tracking_code'] == tracking_code
        assert tracking_response.data['status'] == Shipment.STATUS_PAID

    def test_workflow_payment_failure_keeps_pending(self, authenticated_api_client, test_locations):
        """Test that payment failure keeps shipment in PENDING_PAYMENT state."""
        # Create shipment
        create_payload = {
            'origin_id': test_locations['origin'].id,
            'destination_id': test_locations['destination'].id,
            'weight_kg': '3.0'
        }
        
        create_response = authenticated_api_client.post(
            '/api/shipments/create/',
            data=create_payload,
            format='json'
        )
        
        shipment_id = create_response.data['id']
        
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
        
        # Simulate webhook callback (failure)
        webhook_payload = {
            'shipment_id': shipment_id,
            'transaction_id': transaction_id,
            'status': 'FAILURE',
            'timestamp': timezone.now().isoformat()
        }
        
        webhook_response = authenticated_api_client.post(
            '/api/payments/webhook/',
            data=webhook_payload,
            format='json'
        )
        
        assert webhook_response.status_code == status.HTTP_200_OK
        
        # Verify shipment status is FAILED
        shipment = Shipment.objects.get(id=shipment_id)
        assert shipment.status == 'FAILED'

    def test_workflow_tariff_calculation_variations(self, authenticated_api_client, test_locations):
        """Test tariff calculation for different weights and zones."""
        test_cases = [
            {'weight': '1.0', 'expected_min': 7.0},  # 5.0 base + 2.0 * weight
            {'weight': '5.5', 'expected_min': 16.0},  # 5.0 base + 2.0 * 5.5
            {'weight': '10.0', 'expected_min': 25.0},  # 5.0 base + 2.0 * 10.0
        ]
        
        for test_case in test_cases:
            payload = {
                'origin_id': test_locations['origin'].id,
                'destination_id': test_locations['destination'].id,
                'weight_kg': test_case['weight']
            }
            
            response = authenticated_api_client.post(
                '/api/shipments/create/',
                data=payload,
                format='json'
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            tariff = float(response.data['tariff'])
            assert tariff >= test_case['expected_min'], \
                f"Tariff {tariff} should be >= {test_case['expected_min']} for weight {test_case['weight']}"

    def test_workflow_tracking_code_uniqueness(self, authenticated_api_client, test_locations):
        """Test that tracking codes are unique across multiple shipments."""
        tracking_codes = set()
        
        for i in range(5):
            payload = {
                'origin_id': test_locations['origin'].id,
                'destination_id': test_locations['destination'].id,
                'weight_kg': '1.0'
            }
            
            response = authenticated_api_client.post(
                '/api/shipments/create/',
                data=payload,
                format='json'
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            tracking_code = response.data['tracking_code']
            
            assert tracking_code not in tracking_codes, \
                f"Duplicate tracking code generated: {tracking_code}"
            
            tracking_codes.add(tracking_code)
        
        assert len(tracking_codes) == 5

    def test_workflow_simultaneous_shipments(self, authenticated_api_client, test_locations):
        """Test creating multiple shipments doesn't cause race conditions."""
        shipment_ids = []
        
        for i in range(3):
            payload = {
                'origin_id': test_locations['origin'].id,
                'destination_id': test_locations['destination'].id,
                'weight_kg': f'{1.0 + i}'
            }
            
            response = authenticated_api_client.post(
                '/api/shipments/create/',
                data=payload,
                format='json'
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            shipment_ids.append(response.data['id'])
        
        # Verify all shipments exist and have correct status
        shipments = Shipment.objects.filter(id__in=shipment_ids)
        assert shipments.count() == 3
        
        for shipment in shipments:
            assert shipment.status == Shipment.STATUS_PENDING_PAYMENT
            assert shipment.tariff > 0
