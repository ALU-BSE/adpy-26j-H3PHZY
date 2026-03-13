from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from shipments.models import Shipment
from shipments.services import BookingService
from .serializers import PaymentInitiateSerializer, PaymentStatusSerializer, PaymentWebhookSerializer
from .services import MomoMockGateway


# Global gateway instance (in production, this would be injected/configured)
_momo_gateway = MomoMockGateway()


class PaymentInitiateView(generics.CreateAPIView):
    """Endpoint to initiate a mobile money payment for a shipment."""
    serializer_class = PaymentInitiateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Initiate payment via MomoMockGateway."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipment_id = serializer.validated_data.get('shipment_id')
        phone = serializer.validated_data.get('phone')

        # Validate shipment exists and belongs to user
        try:
            shipment = Shipment.objects.get(id=shipment_id)
        except Shipment.DoesNotExist:
            return Response(
                {'error': 'Shipment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only authenticated user or sender can initiate payment
        if shipment.sender != request.user:
            return Response(
                {'error': 'You do not have permission to pay for this shipment'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Shipment must be in PENDING_PAYMENT state
        if shipment.status != Shipment.STATUS_PENDING_PAYMENT:
            return Response(
                {'error': f'Shipment is in {shipment.status} state, cannot initiate payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Define callback that will be invoked when payment succeeds/fails
        def payment_callback(payload: dict):
            """Callback invoked by the mock gateway upon payment completion."""
            service = BookingService()
            success = payload.get('status') == 'SUCCESS'
            # Update shipment status based on payment result
            service.confirm_payment(shipment, success)

        # Initiate payment via mock gateway
        try:
            tx_id = _momo_gateway.initiate_payment(
                amount=float(shipment.tariff),
                phone=phone,
                callback=payment_callback
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to initiate payment: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Return success response with transaction details
        response_data = {
            'shipment_id': shipment.id,
            'transaction_id': tx_id,
            'status': 'INITIATED',
            'phone': phone,
            'amount': shipment.tariff,
            'message': 'Payment request sent. Awaiting confirmation.'
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class PaymentWebhookView(generics.CreateAPIView):
    """Endpoint to receive payment callbacks from external payment gateways.
    
    This should be called by the payment provider (e.g., MTN/Airtel) when a payment
    succeeds or fails. Allowed publicly since external systems invoke it.
    """
    serializer_class = PaymentWebhookSerializer
    permission_classes = [AllowAny]  # External gateways are not authenticated

    def create(self, request, *args, **kwargs):
        """Process payment webhook callback."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transaction_id = serializer.validated_data.get('transaction_id')
        status_result = serializer.validated_data.get('status')
        timestamp = serializer.validated_data.get('timestamp')
        shipment_id = request.data.get('shipment_id')

        if not shipment_id:
            return Response(
                {'error': 'shipment_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            shipment = Shipment.objects.get(id=shipment_id)
        except Shipment.DoesNotExist:
            return Response(
                {'error': f'Shipment {shipment_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        service = BookingService()
        try:
            updated_shipment = service.confirm_payment(shipment, status_result == 'SUCCESS')
        except Exception as e:
            return Response(
                {'error': f'Failed to process: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'shipment_id': updated_shipment.id,
            'tracking_code': updated_shipment.tracking_code,
            'transaction_id': transaction_id,
            'payment_status': status_result,
            'shipment_status': updated_shipment.status,
            'timestamp': timestamp,
        }, status=status.HTTP_200_OK)
