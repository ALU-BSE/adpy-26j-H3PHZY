from rest_framework import serializers
from .models import InternationalShipment, CustomsDocument


class CustomsDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomsDocument
        fields = (
            'id', 'declaration_number', 'declared_value',
            'origin_country', 'destination_country'
        )


class InternationalShipmentSerializer(serializers.ModelSerializer):
    customs_doc = CustomsDocumentSerializer(read_only=True)
    
    class Meta:
        model = InternationalShipment
        fields = (
            'id', 'tracking_number', 'sender', 'recipient_name', 'recipient_phone',
            'origin_location', 'destination', 'weight_kg', 'description',
            'sender_tin', 'recipient_passport', 'recipient_tin',
            'hs_code', 'customs_value', 'status', 'cost',
            'created_at', 'updated_at', 'customs_doc'
        )
        read_only_fields = ('id', 'tracking_number', 'created_at', 'updated_at')


class InternationalShipmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternationalShipment
        fields = (
            'recipient_name', 'recipient_phone', 'origin_location',
            'destination', 'weight_kg', 'description',
            'sender_tin', 'recipient_passport', 'recipient_tin',
            'hs_code', 'customs_value'
        )
    
    def create(self, validated_data):
        import uuid
        tracking_number = f"RW-INTL-{uuid.uuid4().hex[:8].upper()}"
        
        shipment = InternationalShipment.objects.create(
            tracking_number=tracking_number,
            sender=self.context['request'].user,
            **validated_data
        )
        
        # Create customs document
        CustomsDocument.objects.create(
            intl_shipment=shipment,
            declaration_number=f"CD-{shipment.id}-{uuid.uuid4().hex[:6].upper()}",
            declared_value=validated_data['customs_value'],
            destination_country=self._get_destination_country(validated_data['destination'])
        )
        
        return shipment
    
    @staticmethod
    def _get_destination_country(destination):
        mapping = {
            'KAMPALA': 'UG',
            'NAIROBI': 'KE',
            'GOMA': 'CD',
            'BUJUMBURA': 'BI',
        }
        return mapping.get(destination, 'UG')
