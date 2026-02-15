from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/verify-nid/', views.NIDBatchVerificationView.as_view(), name='verify-nid'),
    # JWT token endpoints
    path('auth/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth_logout'),
    
    # User management
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('users/agents/onboard/', views.AgentOnboardingView.as_view(), name='agent-onboard'),
]
