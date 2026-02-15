from rest_framework import generics, status, filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
import asyncio
from .models import Shipment, ShipmentLog
from .serializers import (
    ShipmentSerializer, ShipmentCreateSerializer, 
    ShipmentStatusUpdateSerializer
)


def _deny_if_unverified(request):
    """Return a 403 Response if the requesting user is not verified."""
    if not getattr(request, 'user', None):
        return None
    if not getattr(request.user, 'is_verified', False):
        return Response({'detail': 'User account is not verified.'}, status=status.HTTP_403_FORBIDDEN)
    return None


class ShipmentListCreateView(generics.ListCreateAPIView):
    """List and create shipments"""
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'origin_location', 'destination_location']
    search_fields = ['tracking_number', 'recipient_name']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ShipmentCreateSerializer
        return ShipmentSerializer
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        resp = _deny_if_unverified(request)
        if resp:
            return resp
        return super().dispatch(request, *args, **kwargs)


class ShipmentDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update shipment details"""
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'tracking_number'

    def dispatch(self, request, *args, **kwargs):
        resp = _deny_if_unverified(request)
        if resp:
            return resp
        return super().dispatch(request, *args, **kwargs)


class ShipmentTrackingView(generics.GenericAPIView):
    """Get full tracking history"""
    permission_classes = [IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        resp = _deny_if_unverified(request)
        if resp:
            return resp
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, tracking_number):
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
            logs = ShipmentLog.objects.filter(shipment=shipment).order_by('-timestamp')
            
            return Response({
                'tracking_number': shipment.tracking_number,
                'status': shipment.status,
                'recipient': shipment.recipient_name,
                'weight_kg': shipment.weight_kg,
                'cost': shipment.cost,
                'created_at': shipment.created_at,
                'updated_at': shipment.updated_at,
                'tracking_history': [
                    {
                        'status': log.status,
                        'location': log.location.name if log.location else None,
                        'notes': log.notes,
                        'timestamp': log.timestamp
                    }
                    for log in logs
                ]
            })
        except Shipment.DoesNotExist:
            return Response(
                {'error': 'Shipment not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ShipmentStatusUpdateView(generics.GenericAPIView):
    """Update shipment status (Async)"""
    serializer_class = ShipmentStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        resp = _deny_if_unverified(request)
        if resp:
            return resp
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, tracking_number):
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
        except Shipment.DoesNotExist:
            return Response(
                {'error': 'Shipment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update status
        shipment.status = serializer.validated_data['status']
        shipment.save()
        
        # Create log entry
        location_id = serializer.validated_data.get('location_id')
        location = None
        if location_id:
            try:
                from core.models import Location
                location = Location.objects.get(id=location_id)
            except:
                pass
        
        ShipmentLog.objects.create(
            shipment=shipment,
            status=shipment.status,
            location=location,
            notes=serializer.validated_data.get('notes', ''),
            logged_by=request.user
        )
        
        return Response({
            'tracking_number': shipment.tracking_number,
            'status': shipment.status,
            'message': 'Status updated successfully'
        })


class ShipmentBatchUpdateView(generics.GenericAPIView):
    """Update multiple shipments at once"""
    permission_classes = [IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        resp = _deny_if_unverified(request)
        if resp:
            return resp
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """
        Expect JSON like:
        {
            "updates": [
                {"tracking_number": "RW-001", "status": "IN_TRANSIT", "notes": "Left warehouse"},
                ...
            ]
        }
        """
        updates = request.data.get('updates', [])
        
        if not updates:
            return Response(
                {'error': 'No updates provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process updates asynchronously (simulated)
        processed = 0
        failed = 0
        
        for update in updates:
            try:
                shipment = Shipment.objects.get(tracking_number=update['tracking_number'])
                shipment.status = update.get('status', shipment.status)
                shipment.save()
                
                ShipmentLog.objects.create(
                    shipment=shipment,
                    status=shipment.status,
                    notes=update.get('notes', ''),
                    logged_by=request.user
                )
                
                processed += 1
            except Exception as e:
                failed += 1
                print(f"Error updating {update.get('tracking_number')}: {str(e)}")
        
        return Response({
            'message': f'Batch update completed',
            'processed': processed,
            'failed': failed,
            'total': len(updates),
            'status': 'queued'
        })
