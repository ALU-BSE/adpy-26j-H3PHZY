from django.urls import path
from . import views, ops_views, test_views

urlpatterns = [
    # Authentication
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.UserLoginView.as_view(), name='login'),
    path('auth/verify-nid/', views.NIDBatchVerificationView.as_view(), name='verify-nid'),
    
    # User management
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('users/agents/onboard/', views.AgentOnboardingView.as_view(), name='agent-onboard'),
    
    # Admin & Ops
    path('admin/dashboard/summary/', views.DashboardSummaryView.as_view(), name='admin-dashboard-summary'),
    path('health/deep/', ops_views.DeepHealthCheckView.as_view(), name='deep-health-check'),
    path('ops/metrics/', ops_views.PrometheusMetricsView.as_view(), name='prometheus-metrics'),
    path('ops/maintenance/toggle/', ops_views.MaintenanceToggleView.as_view(), name='maintenance-toggle'),
    
    # Testing (National Rollout Task 2)
    path('test/seed/', test_views.SeedTestDataView.as_view(), name='test-seed'),
    path('test/load-simulation/', test_views.LoadSimulationView.as_view(), name='load-simulation'),
    path('test/security-health/', test_views.SecurityHealthView.as_view(), name='security-health'),
]
