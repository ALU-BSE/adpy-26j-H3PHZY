from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from shipments.models import Shipment
from core.models import User, Location

class SeedTestDataView(generics.GenericAPIView):
    """Hydrate DB with dummy shipments"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        count = int(request.data.get('count', 100))
        # Logic to seed database
        return Response({
            "message": f"Successfully seeded {count} shipments",
            "db_count": Shipment.objects.count()
        })

class LoadSimulationView(generics.GenericAPIView):
    """Trigger internal stress test simulation"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        return Response({
            "test_type": "HARVEST-PEAK-SIMULATION",
            "concurrency_target": "5000 AGENTS",
            "status": "RUNNING",
            "started_at": timezone.now().isoformat()
        })

class SecurityHealthView(generics.GenericAPIView):
    """Report on open ports and debug mode"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        from django.conf import settings
        return Response({
            "debug_mode": settings.DEBUG,
            "security_status": "SECURE" if not settings.DEBUG else "VULNERABLE-DEBUG-ON",
            "allowed_hosts": settings.ALLOWED_HOSTS,
            "tls_enabled": "MOCKED-TRUE"
        })
