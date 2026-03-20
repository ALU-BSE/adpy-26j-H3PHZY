from rest_framework import serializers
from .models import Shipment


class ShipmentSerializer(serializers.ModelSerializer):
    """Serializer for shipment creation and retrieval."""
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    origin_name = serializers.CharField(source='origin.name', read_only=True)
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    driver_username = serializers.CharField(source='driver.username', read_only=True, allow_null=True)

    class Meta:
        model = Shipment
        fields = [
            'id', 'tracking_code', 'sender', 'sender_username',
            'origin', 'origin_name', 'destination', 'destination_name',
            'tariff', 'status', 'driver', 'driver_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tracking_code', 'tariff', 'created_at', 'updated_at']


class ShipmentCreateSerializer(serializers.Serializer):
    """Serializer for creating a new shipment with minimal required fields."""
    origin_id = serializers.IntegerField(required=True, help_text="Location ID for origin")
    destination_id = serializers.IntegerField(required=True, help_text="Location ID for destination")
    weight_kg = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_weight_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be greater than 0 kg")
        return value


class TrackingLocationSerializer(serializers.Serializer):
    """Serializer for a single location in tracking history."""
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    address = serializers.CharField(required=False, allow_blank=True)


class TrackingLiveSerializer(serializers.Serializer):
    """Serializer for live tracking response."""
    tracking_code = serializers.CharField()
    status = serializers.CharField()
    current_location = TrackingLocationSerializer()
    destination = serializers.CharField()
    driver = serializers.CharField(allow_null=True, required=False)
    estimated_arrival = serializers.DateTimeField(required=False, allow_null=True)
    last_update = serializers.DateTimeField()
