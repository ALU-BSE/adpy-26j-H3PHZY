from rest_framework import serializers
from shipments.models import Shipment


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating a payment request."""
    shipment_id = serializers.IntegerField(required=True, help_text="Shipment ID to pay for")
    phone = serializers.CharField(max_length=13, required=True, help_text="Mobile money phone number (e.g., +250799123456)")

    def validate_phone(self, value):
        """Validate phone format (simple Rwanda check)."""
        if not value.startswith('+250'):
            raise serializers.ValidationError("Phone must be in format +250XXXXXXXXX")
        if len(value) != 13:
            raise serializers.ValidationError("Phone must be exactly 13 characters (+250 + 10 digits)")
        # Check that remaining characters are digits
        digits_part = value[4:]  # Skip '+250'
        if not digits_part.isdigit():
            raise serializers.ValidationError("Phone must contain only digits after +250")
        return value


class PaymentStatusSerializer(serializers.Serializer):
    """Serializer for payment status response."""
    shipment_id = serializers.IntegerField()
    transaction_id = serializers.CharField()
    status = serializers.CharField()
    phone = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    message = serializers.CharField(required=False)


class PaymentWebhookSerializer(serializers.Serializer):
    """Serializer for receiving payment webhook callbacks from payment gateway."""
    transaction_id = serializers.CharField(max_length=50)
    status = serializers.CharField(max_length=20, help_text="SUCCESS or FAILURE")
    timestamp = serializers.DateTimeField()

    def validate_status(self, value):
        """Ensure status is SUCCESS or FAILURE."""
        if value not in ['SUCCESS', 'FAILURE']:
            raise serializers.ValidationError(f"Status must be SUCCESS or FAILURE, got {value}")
        return value
