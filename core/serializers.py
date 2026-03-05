from rest_framework import serializers
from django.contrib.auth import get_user_model
from .validators import validate_rwanda_phone, validate_rwanda_nid

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 
                  'user_type', 'assigned_sector', 'is_verified', 'created_at')
        read_only_fields = ('id', 'created_at', 'is_verified')


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'phone', 
                  'first_name', 'last_name', 'user_type', 'assigned_sector', 'national_id')
    
    def validate_phone(self, value):
        """Validate phone number format"""
        is_valid, message = validate_rwanda_phone(value)
        if not is_valid:
            raise serializers.ValidationError(message)
        return value
    
    def validate_national_id(self, value):
        """Validate national ID if provided"""
        if value:
            is_valid, message = validate_rwanda_nid(value)
            if not is_valid:
                raise serializers.ValidationError(message)
        return value
    
    def validate(self, data):
        """Validate password confirmation"""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        return data
    
    def create(self, validated_data):
        """Create user with validated data"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone',
                  'user_type', 'assigned_sector', 'national_id', 'is_verified', 'created_at')
        read_only_fields = ('id', 'created_at', 'is_verified')


class NIDBatchVerificationSerializer(serializers.Serializer):
    """Serializer for batch NID verification"""
    nid = serializers.CharField(max_length=16, min_length=16)
    
    def validate_nid(self, value):
        is_valid, message = validate_rwanda_nid(value)
        if not is_valid:
            raise serializers.ValidationError(message)
        return value


# JWT Custom serializer to include `user_type` claim
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claim
        token['user_type'] = getattr(user, 'user_type', None)
        return token
