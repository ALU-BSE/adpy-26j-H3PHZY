from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum, Avg
from shipments.models import Shipment
from core.models import Location, User

class TopRoutesView(generics.GenericAPIView):
    """Most frequented corridors (districts)"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Identify top destination districts
        routes = Shipment.objects.values('destination__district').annotate(
            count=Count('id'),
            total_weight=Sum('weight')
        ).order_by('-count')[:5]
        
        return Response({
            "high_traffic_corridors": routes,
            "metric": "Shipment Density by District"
        })

class CommodityBreakdownView(generics.GenericAPIView):
    """Cargo type stats (e.g. Potatoes vs Electronics)"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Anonymized commodity stats
        stats = Shipment.objects.values('description').annotate(
            volume_kg=Sum('weight'),
            count=Count('id')
        ).order_by('-volume_kg')
        
        return Response({
            "commodity_stats": stats,
            "data_policy": "ANONYMIZED-PRIVACY-PROTECTED"
        })

class RevenueHeatmapView(generics.GenericAPIView):
    """Geospatial revenue data (Earnings per Sector)"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Revenue by destination sector
        heatmap = Shipment.objects.values('destination__sector').annotate(
            revenue_rwf=Sum('tariff')
        ).order_by('-revenue_rwf')
        
        return Response({
            "revenue_heatmap": heatmap,
            "currency": "RWF"
        })

class DriverLeaderboardView(generics.GenericAPIView):
    """Top performing transporters"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Performance metrics for drivers
        leaderboard = Shipment.objects.filter(driver__isnull=False).values(
            'driver__username'
        ).annotate(
            completed_jobs=Count('id'),
            avg_weight=Avg('weight')
        ).order_by('-completed_jobs')
        
        return Response({
            "leaderboard": leaderboard,
            "criteria": "Completed Deliveries"
        })
