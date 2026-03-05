from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import secrets
import datetime

# OTP settings (can be overridden in Django settings)
OTP_EXPIRY_SECONDS = getattr(settings, 'OTP_EXPIRY_SECONDS', 300)  # 5 minutes
OTP_MAX_ATTEMPTS = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)


# Reuse the registration serializer from core
from core.serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()


class IdentityRegisterView(generics.CreateAPIView):
	"""Register a new user at /api/identity/register/.

	Ensures `is_verified` is False by default regardless of input.
	"""
	serializer_class = UserRegistrationSerializer
	permission_classes = [AllowAny]

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()

		# Enforce is_verified=False explicitly
		if getattr(user, 'is_verified', None):
			user.is_verified = False
			user.save(update_fields=['is_verified'])

		output = UserSerializer(user)
		return Response(output.data, status=status.HTTP_201_CREATED)


class RequestOTPView(generics.GenericAPIView):
	"""Request a one-time 6-digit code. Stored in cache and expires in 5 minutes.

	POST body: { "phone": "+2507..." } or { "username": "alice" }
	"""
	permission_classes = [AllowAny]
	serializer_class = None

	def post(self, request):
		from .serializers import RequestOTPSerializer
		serializer = RequestOTPSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		phone = serializer.validated_data.get('phone')
		username = serializer.validated_data.get('username')

		# Resolve username -> phone if username provided
		if not phone and username:
			try:
				user = User.objects.get(username=username)
				phone = getattr(user, 'phone', None)
			except User.DoesNotExist:
				phone = None

		if not phone:
			return Response({'detail': 'Phone not found or provided.'}, status=status.HTTP_400_BAD_REQUEST)

		# Generate secure 6-digit code
		code = ''.join(str(secrets.randbelow(10)) for _ in range(6))

		otp_key = f"otp:{phone}"
		attempts_key = f"otp_attempts:{phone}"
		used_key = f"otp_used:{phone}:{code}"

		# Store code and a used flag is false; cache will expire the code
		cache.set(otp_key, code, timeout=OTP_EXPIRY_SECONDS)
		cache.set(attempts_key, 0, timeout=OTP_EXPIRY_SECONDS)

		# In a real system, send via SMS. Here we return the code for simulation.
		return Response({
			'phone': phone,
			'otp': code,
			'expires_in': OTP_EXPIRY_SECONDS
		}, status=status.HTTP_200_OK)


class VerifyOTPView(generics.GenericAPIView):
	"""Verify an OTP previously issued. Prevents reuse and enforces retry limits."""
	permission_classes = [AllowAny]
	serializer_class = None

	def post(self, request):
		from .serializers import VerifyOTPSerializer
		serializer = VerifyOTPSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		phone = serializer.validated_data.get('phone')
		username = serializer.validated_data.get('username')
		code = serializer.validated_data.get('code')

		# Resolve username -> phone if username provided
		if not phone and username:
			try:
				user = User.objects.get(username=username)
				phone = getattr(user, 'phone', None)
			except User.DoesNotExist:
				phone = None

		if not phone:
			return Response({'detail': 'Phone not found or provided.'}, status=status.HTTP_400_BAD_REQUEST)

		otp_key = f"otp:{phone}"
		attempts_key = f"otp_attempts:{phone}"
		used_key = f"otp_used:{phone}:{code}"

		# Ensure OTP exists
		stored = cache.get(otp_key)
		if not stored:
			return Response({'detail': 'OTP expired or not found.'}, status=status.HTTP_400_BAD_REQUEST)

		# Prevent reuse: check used key
		if cache.get(used_key):
			return Response({'detail': 'OTP already used.'}, status=status.HTTP_400_BAD_REQUEST)

		# Enforce retry attempts
		attempts = cache.get(attempts_key) or 0
		if attempts >= OTP_MAX_ATTEMPTS:
			return Response({'detail': 'Max OTP verification attempts exceeded.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

		if secrets.compare_digest(str(stored), str(code)):
			# Mark as used and delete the otp key to prevent reuse
			cache.set(used_key, True, timeout=OTP_EXPIRY_SECONDS)
			cache.delete(otp_key)
			cache.delete(attempts_key)
			return Response({'detail': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
		else:
			# Increment attempts
			cache.incr(attempts_key)
			remaining = OTP_MAX_ATTEMPTS - (attempts + 1)
			return Response({'detail': 'Invalid OTP.', 'remaining_attempts': max(0, remaining)}, status=status.HTTP_400_BAD_REQUEST)
