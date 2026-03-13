from rest_framework import serializers
from .models import Zone, Tariff
from decimal import Decimal


class TariffSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    
    class Meta:
        model = Tariff
        fields = ('id', 'zone', 'zone_name', 'weight_from_kg', 'weight_to_kg', 'base_rate', 'per_kg_rate', 'active')


class ZoneSerializer(serializers.ModelSerializer):
    tariffs = TariffSerializer(many=True, read_only=True)
    
    class Meta:
        model = Zone
        fields = ('id', 'zone_number', 'name', 'description', 'coverage_areas', 'tariffs')


class PricingCalculatorSerializer(serializers.Serializer):
    zone_id = serializers.IntegerField()
    weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('0.1'))
    
    def validate_weight_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be greater than 0")
        return value
