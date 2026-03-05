from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    NIDBatchVerificationSerializer
)
from .validators import validate_rwanda_nid

User = get_user_model()


class HealthCheckView(generics.GenericAPIView):
    """System health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Check system health and database connectivity"""
        from django.db import connection
        try:
            connection.ensure_connection()
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return Response({
            "status": "healthy",
            "database": db_status,
            "version": "1.0.0"
        })


class APIRootView(generics.GenericAPIView):
    """API root with version information"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            "api_version": "1.0.0",
            "project": "IshemaLink",
            "description": "Logistics API for Rwanda cross-border trade",
            "endpoints": {
                "health": "/api/status/",
                "auth": {
                    "register": "/api/auth/register/",
                    "verify_nid": "/api/auth/verify-nid/",
                    "profile": "/api/users/me/"
                },
                "shipments": "/api/shipments/",
                "pricing": "/api/pricing/"
            }
        })


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        response_serializer = UserSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class NIDBatchVerificationView(generics.GenericAPIView):
    """Verify National ID"""
    serializer_class = NIDBatchVerificationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        nid = serializer.validated_data['nid']
        is_valid, message = validate_rwanda_nid(nid)

        payload = {"nid": nid, "valid": is_valid}
        if not is_valid:
            payload["error"] = message
        return Response(payload)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get/Update current user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class AgentOnboardingView(generics.CreateAPIView):
    """Special endpoint for Agent onboarding (requires NID)"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        # copy payload to avoid mutating original (works with JSON too)
        data = request.data.copy()
        data['user_type'] = 'AGENT'

        # NID is required for agents
        if not data.get('national_id'):
            return Response(
                {"error": "National ID is required for agent onboarding"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        response_serializer = UserSerializer(user)
        return Response({
            **response_serializer.data,
            "message": "Agent registered successfully. Please await verification."
        }, status=status.HTTP_201_CREATED)


# --- JWT auth views (custom token claims + logout blacklist + rate limit) ---
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Issue JWT tokens and include custom claims. Rate-limited by 'login' scope."""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    throttle_scope = 'login'


class LogoutView(APIView):
    """Blacklist refresh token on logout to invalidate it.

    This view allows unauthenticated clients to send a refresh token to be
    blacklisted (useful for mobile logout where only a refresh token is held).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
