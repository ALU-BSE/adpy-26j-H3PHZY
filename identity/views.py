from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model

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
