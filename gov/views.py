from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .services import RRAConnector, RURAConnector, CustomsService
from shipments.models import Shipment

class EBMSignReceiptView(generics.GenericAPIView):
    """Request tax signature from RRA"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        shipment_id = request.data.get('shipment_id')
        amount = request.data.get('amount')
        
        if not shipment_id or not amount:
            return Response({'error': 'shipment_id and amount are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        result = RRAConnector.sign_receipt(shipment_id, amount)
        return Response(result)

class RURAVerifyLicenseView(generics.GenericAPIView):
    """Verify driver/truck status via RURA"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, license_no):
        result = RURAConnector.verify_transport_license(license_no)
        return Response(result)

class CustomsManifestView(generics.GenericAPIView):
    """Generate EAC-compliant Customs Manifest XML"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        shipment_id = request.data.get('shipment_id')
        try:
            shipment = Shipment.objects.get(id=shipment_id)
        except Shipment.DoesNotExist:
            return Response({'error': 'Shipment not found'}, status=status.HTTP_404_NOT_FOUND)
            
        xml_data = CustomsService.generate_manifest_xml(shipment)
        return Response({
            "xml_manifest": xml_data,
            "format": "EAC-XML-v1",
            "status": "GENERATED"
        })

class GovAuditLogView(generics.GenericAPIView):
    """Government-specific audit trail"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Mock audit trail
        return Response({
            "audit_log": [
                {"timestamp": "2026-02-23T10:00:00Z", "action": "EBM_SIGN", "user": "agent_alpha", "shipment": "RW-001"},
                {"timestamp": "2026-02-23T11:30:00Z", "action": "RURA_VERIFY", "user": "admin", "license": "RW-T-123"},
                {"timestamp": "2026-02-23T12:00:00Z", "action": "MANIFEST_GEN", "user": "agent_beta", "shipment": "RW-002"}
            ]
        })
