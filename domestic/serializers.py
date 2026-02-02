from rest_framework import serializers
from .models import Shipment, ShipmentLog
from decimal import Decimal


class ShipmentLogSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = ShipmentLog
        fields = ('id', 'status', 'location', 'location_name', 'notes', 'logged_by', 'timestamp')
        read_only_fields = ('id', 'logged_by', 'timestamp')


class ShipmentSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    origin_name = serializers.CharField(source='origin_location.name', read_only=True)
    destination_name = serializers.CharField(source='destination_location.name', read_only=True)
    logs = ShipmentLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Shipment
        fields = (
            'id', 'tracking_number', 'sender', 'sender_name', 'recipient_name', 'recipient_phone',
            'origin_location', 'origin_name', 'destination_location', 'destination_name',
            'weight_kg', 'description', 'status', 'cost', 'created_at', 'updated_at', 'logs'
        )
        read_only_fields = ('id', 'tracking_number', 'sender', 'created_at', 'updated_at')


class ShipmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = (
            'recipient_name', 'recipient_phone', 'origin_location', 'destination_location',
            'weight_kg', 'description', 'cost'
        )
    
    def create(self, validated_data):
        import uuid
        tracking_number = f"RW-{uuid.uuid4().hex[:8].upper()}"
        
        shipment = Shipment.objects.create(
            tracking_number=tracking_number,
            sender=self.context['request'].user,
            **validated_data
        )
        
        return shipment


class ShipmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        'PENDING', 'IN_TRANSIT', 'ARRIVED_HUB', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED'
    ])
    location_id = serializers.IntegerField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
from .models import Shipment, ShipmentLog
from core.models import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'location_type', 'code')


class ShipmentLogSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    
    class Meta:
        model = ShipmentLog
        fields = ('id', 'status', 'location', 'notes', 'timestamp')


class ShipmentSerializer(serializers.ModelSerializer):
    origin_location = LocationSerializer(read_only=True)
    destination_location = LocationSerializer(read_only=True)
    logs = ShipmentLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Shipment
        fields = (
            'id', 'tracking_number', 'sender', 'recipient_name', 'recipient_phone',
            'origin_location', 'destination_location', 'weight_kg', 'description',
            'status', 'cost', 'created_at', 'updated_at', 'logs'
        )
        read_only_fields = ('id', 'tracking_number', 'created_at', 'updated_at')


class ShipmentCreateSerializer(serializers.ModelSerializer):
    origin_location_id = serializers.IntegerField()
    destination_location_id = serializers.IntegerField()
    
    class Meta:
        model = Shipment
        fields = (
            'recipient_name', 'recipient_phone', 'origin_location_id',
            'destination_location_id', 'weight_kg', 'description'
        )
    
    def create(self, validated_data):
        # Generate tracking number
        import uuid
        tracking_number = f"RW-{uuid.uuid4().hex[:8].upper()}"
        
        shipment = Shipment.objects.create(
            tracking_number=tracking_number,
            sender=self.context['request'].user,
            **validated_data
        )
        return shipment


class ShipmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Shipment.STATUS_CHOICES)
    location_id = serializers.IntegerField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
