from rest_framework import serializers


class RequestOTPSerializer(serializers.Serializer):
    """Serializer for requesting an OTP. Identify user by `phone` or `username`."""
    phone = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if not data.get('phone') and not data.get('username'):
            raise serializers.ValidationError('Provide either phone or username.')
        return data


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField()

    def validate(self, data):
        if not data.get('phone') and not data.get('username'):
            raise serializers.ValidationError('Provide either phone or username.')
        if not data.get('code'):
            raise serializers.ValidationError('OTP code is required.')
        return data
