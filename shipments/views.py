from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
import random

from core.models import Location
from .models import Shipment
from .serializers import ShipmentCreateSerializer, ShipmentSerializer, TrackingLiveSerializer
from .services import BookingService


class ShipmentCreateView(generics.CreateAPIView):
    """Endpoint to create a new shipment and initiate the booking workflow."""
    serializer_class = ShipmentCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create a new shipment."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        origin_id = serializer.validated_data.get('origin_id')
        destination_id = serializer.validated_data.get('destination_id')
        weight_kg = serializer.validated_data.get('weight_kg')
        description = serializer.validated_data.get('description', '')

        try:
            origin = Location.objects.get(id=origin_id)
            destination = Location.objects.get(id=destination_id)
        except Location.DoesNotExist as e:
            return Response(
                {'error': f'Location not found: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = BookingService()
        try:
            shipment = service.create_shipment(
                sender=request.user,
                origin=origin,
                destination=destination,
                weight_kg=weight_kg,
                description=description
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create shipment: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED)


class TrackingLiveView(generics.GenericAPIView):
    """Endpoint to retrieve real-time tracking information for a shipment.
    
    Returns current location (mock coordinates), status, and ETA.
    In production, this would integrate with GPS/GSM tracking devices.
    For now, returns simulated coordinates within Rwanda.
    """
    serializer_class = TrackingLiveSerializer
    permission_classes = [AllowAny]  # Tracking is publicly accessible
    lookup_field = 'tracking_code'
    lookup_url_kwarg = 'tracking_code'

    def get(self, request, *args, **kwargs):
        """Get live tracking for shipment by tracking code."""
        tracking_code = kwargs.get('tracking_code')
        
        # Find shipment by tracking code
        try:
            shipment = Shipment.objects.get(tracking_code=tracking_code)
        except Shipment.DoesNotExist:
            return Response(
                {'error': f'Shipment with tracking code {tracking_code} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate mock coordinates
        # Simulating a truck moving from origin to destination
        # Base coordinates in Rwanda (Kigali area)
        base_lat = -1.9536
        base_lng = 29.8739
        
        # Add random offset to simulate movement
        offset_lat = random.uniform(-0.1, 0.1)  # ~11km variation
        offset_lng = random.uniform(-0.1, 0.1)  # ~11km variation
        
        current_lat = base_lat + offset_lat
        current_lng = base_lng + offset_lng
        
        # Build response
        tracking_data = {
            'tracking_code': shipment.tracking_code,
            'status': shipment.status,
            'current_location': {
                'latitude': current_lat,
                'longitude': current_lng,
                'timestamp': timezone.now(),
                'address': f"En route (Mock coordinates in Rwanda)"
            },
            'destination': shipment.destination.name if shipment.destination else 'Unknown',
            'driver': shipment.driver.username if shipment.driver else None,
            'last_update': timezone.now(),
        }
        
        # If shipment is dispatched, estimate arrival
        if shipment.status == Shipment.STATUS_DISPATCHED:
            from datetime import timedelta
            tracking_data['estimated_arrival'] = timezone.now() + timedelta(hours=2)
        
        serializer = self.get_serializer(tracking_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
