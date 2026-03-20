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


class ShipmentDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update shipment details"""
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'tracking_number'


class ShipmentTrackingView(generics.GenericAPIView):
    """Get full tracking history"""
    permission_classes = [IsAuthenticated]
    
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


from notifications.tasks import send_shipment_notification, process_batch_status_update

class ShipmentStatusUpdateView(generics.GenericAPIView):
    """Update shipment status (Async)"""
    serializer_class = ShipmentStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    
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
        
        old_status = shipment.status
        new_status = serializer.validated_data['status']
        
        # Update status
        shipment.status = new_status
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
        
        # Trigger async notification via notifications app
        msg = f"Your shipment {shipment.tracking_number} status is now {new_status}."
        send_shipment_notification.delay(
            shipment.recipient_phone,
            msg,
            shipment.tracking_number
        )
        
        return Response({
            'tracking_number': shipment.tracking_number,
            'status': shipment.status,
            'message': 'Status updated and notification queued'
        })


class ShipmentBatchUpdateView(generics.GenericAPIView):
    """Update multiple shipments at once via Celery"""
    permission_classes = [IsAuthenticated]
    
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
        
        # Offload batch processing to Celery task in notifications app
        task = process_batch_status_update.delay(updates, request.user.id)
        
        return Response({
            'message': f'Batch update queued',
            'task_id': task.id,
            'total_items': len(updates),
            'status': 'queued'
        }, status=status.HTTP_202_ACCEPTED)
