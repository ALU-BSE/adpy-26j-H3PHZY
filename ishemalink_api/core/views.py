from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .validators import validate_phone, validate_nid
from rest_framework.serializers import Serializer, CharField

class UserRegistrationSerializer(Serializer):
    username = CharField(max_length=150)
    password = CharField(max_length=128)
    phone = CharField(max_length=13)
    user_type = CharField(max_length=10)
    assigned_sector = CharField(max_length=100, required=False)

    def validate(self, data):
        if not validate_phone(data['phone']):
            raise serializers.ValidationError({'phone': 'Invalid phone number format.'})
        return data

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            phone=serializer.validated_data['phone'],
            user_type=serializer.validated_data['user_type'],
            assigned_sector=serializer.validated_data.get('assigned_sector')
        )
        return Response({'id': user.id, 'phone': user.phone, 'role': user.user_type}, status=status.HTTP_201_CREATED)

class NIDVerificationView(generics.GenericAPIView):
    class NIDSerializer(Serializer):
        nid = CharField(max_length=16)

    serializer_class = NIDSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valid = validate_nid(serializer.validated_data['nid'])
        return Response({'valid': valid, 'error': 'Invalid NID format. Must be 16 numeric digits starting with 1.' if not valid else None})
