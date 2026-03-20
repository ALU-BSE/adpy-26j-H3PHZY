import os
import shutil
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.db import connection
from django.core.cache import cache

class DeepHealthCheckView(generics.GenericAPIView):
    """Checks DB, Redis, and Disk Space"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        health = {"status": "healthy", "checks": {}}
        
        # 1. Database Check
        try:
            connection.ensure_connection()
            health["checks"]["database"] = "OK"
        except Exception as e:
            health["checks"]["database"] = f"CRITICAL: {str(e)}"
            health["status"] = "unhealthy"
            
        # 2. Redis/Cache Check
        try:
            cache.set("health_check_ping", "pong", 5)
            if cache.get("health_check_ping") == "pong":
                health["checks"]["cache"] = "OK"
            else:
                health["checks"]["cache"] = "DEGRADED"
        except Exception as e:
            health["checks"]["cache"] = f"CRITICAL: {str(e)}"
            
        # 3. Disk Space Check
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (2**30)
        health["checks"]["disk_space"] = f"{free_gb}GB free"
        if free_gb < 1:
            health["status"] = "degraded"
            
        return Response(health, status=status.HTTP_200_OK if health["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE)

class PrometheusMetricsView(generics.GenericAPIView):
    """Prometheus formatted metrics"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Mock Prometheus format
        metrics = [
            "# HELP ishemalink_request_latency_seconds Average request latency",
            "# TYPE ishemalink_request_latency_seconds gauge",
            "ishemalink_request_latency_seconds 0.124",
            "# HELP ishemalink_active_connections Current active connections",
            "# TYPE ishemalink_active_connections counter",
            "ishemalink_active_connections 42"
        ]
        return Response("\n".join(metrics), content_type="text/plain")

class MaintenanceToggleView(generics.GenericAPIView):
    """Switch to 'Under Maintenance' mode"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        current_status = cache.get("maintenance_mode", False)
        new_status = not current_status
        cache.set("maintenance_mode", new_status)
        
        return Response({
            "maintenance_mode": new_status,
            "message": "System is now in MAINTENANCE mode" if new_status else "System is now OPERATIONAL"
        })
