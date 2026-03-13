from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import InternationalShipment
from .serializers import InternationalShipmentSerializer, InternationalShipmentCreateSerializer


class InternationalShipmentListCreateView(generics.ListCreateAPIView):
    """List and create international shipments"""
    queryset = InternationalShipment.objects.all()
    serializer_class = InternationalShipmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['destination', 'status']
    search_fields = ['tracking_number', 'recipient_name', 'sender_tin']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InternationalShipmentCreateSerializer
        return InternationalShipmentSerializer
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class InternationalShipmentDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update international shipment details"""
    queryset = InternationalShipment.objects.all()
    serializer_class = InternationalShipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'tracking_number'


class InternationalShipmentTrackingView(generics.GenericAPIView):
    """Get international shipment tracking with customs status"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, tracking_number):
        try:
            shipment = InternationalShipment.objects.get(tracking_number=tracking_number)
            
            customs_doc = shipment.customs_doc
            
            return Response({
                'tracking_number': shipment.tracking_number,
                'destination': shipment.destination,
                'status': shipment.status,
                'recipient': shipment.recipient_name,
                'weight_kg': shipment.weight_kg,
                'customs_value': shipment.customs_value,
                'cost': shipment.cost,
                'customs_status': {
                    'declaration_number': customs_doc.declaration_number,
                    'declared_value': customs_doc.declared_value,
                    'origin_country': customs_doc.origin_country,
                    'destination_country': customs_doc.destination_country,
                },
                'created_at': shipment.created_at,
                'updated_at': shipment.updated_at,
            })
        except InternationalShipment.DoesNotExist:
            return Response(
                {'error': 'International shipment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
