from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.core.cache import cache
from .models import Zone, Tariff
from .serializers import ZoneSerializer, TariffSerializer, PricingCalculatorSerializer


class TariffListView(generics.ListAPIView):
    """Get current tariffs (Cached)"""
    queryset = Tariff.objects.filter(active=True)
    serializer_class = TariffSerializer
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        # Check cache first
        cache_key = 'tariffs_list'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            response = Response({
                'cached': True,
                'cached_at': cached_data['cached_at'],
                'tariffs': cached_data['tariffs']
            })
            response['X-Cache-Hit'] = 'TRUE'
            return response
        
        # Get from database
        tariffs = self.get_queryset()
        serializer = self.get_serializer(tariffs, many=True)
        
        from datetime import datetime
        cached_data = {
            'cached_at': datetime.now().isoformat(),
            'tariffs': serializer.data
        }
        
        # Cache for 24 hours
        cache.set(cache_key, cached_data, 60 * 60 * 24)
        
        response = Response({
            'cached': False,
            'cached_at': cached_data['cached_at'],
            'tariffs': serializer.data
        })
        response['X-Cache-Hit'] = 'FALSE'
        return response


class ZoneListView(generics.ListAPIView):
    """List all zones with their tariffs"""
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [AllowAny]


class PricingCalculateView(generics.GenericAPIView):
    """Calculate shipping cost for specific weight/destination"""
    serializer_class = PricingCalculatorSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        zone_id = serializer.validated_data['zone_id']
        weight_kg = serializer.validated_data['weight_kg']
        
        try:
            zone = Zone.objects.get(id=zone_id)
        except Zone.DoesNotExist:
            return Response(
                {'error': 'Zone not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find applicable tariff
        tariff = Tariff.objects.filter(
            zone=zone,
            weight_from_kg__lte=weight_kg,
            weight_to_kg__gte=weight_kg,
            active=True
        ).first()
        
        if not tariff:
            return Response(
                {'error': 'No tariff available for this weight/zone combination'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cost = tariff.calculate_cost(weight_kg)
        
        return Response({
            'zone': zone.name,
            'weight_kg': float(weight_kg),
            'base_rate': float(tariff.base_rate),
            'per_kg_rate': float(tariff.per_kg_rate),
            'total_cost_rwf': float(cost),
            'calculation': f"{tariff.base_rate} + ({weight_kg - 1} * {tariff.per_kg_rate})" if weight_kg > 1 else "base_rate"
        })


class CacheClearView(generics.GenericAPIView):
    """Clear pricing cache"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        cache.delete('tariffs_list')
        return Response({
            'message': 'Tariff cache cleared successfully',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
