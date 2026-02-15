from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from core.views import HealthCheckView, APIRootView

router = DefaultRouter()

urlpatterns = [
    # Redirect root to the API root for convenience
    path("", RedirectView.as_view(url='/api/', permanent=False)),
    path("admin/", admin.site.urls),
    
    # Health and status
    path("api/status/", HealthCheckView.as_view(), name='health-check'),
    path("api/", APIRootView.as_view(), name='api-root'),
    
    # API endpoints
    path("api/", include("core.urls")),
    path("api/shipments/", include("domestic.urls")),
    path("api/international/", include("international.urls")),
    path("api/pricing/", include("billing.urls")),
    path("api/identity/", include("identity.urls")),
    path("api/privacy/", include("privacy.urls")),
]
