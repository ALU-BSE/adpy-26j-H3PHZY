from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from core.views import HealthCheckView, APIRootView

router = DefaultRouter()

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Redirect root to documentation
    path("", RedirectView.as_view(url='/api/v1/docs/', permanent=False)),
    path("admin/", admin.site.urls),
    
    # OpenAPI Schema
    path("api/schema/", SpectacularAPIView.as_view(), name='schema'),
    
    # Optional UI:
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Functional API (v1)
    path("api/v1/status/", HealthCheckView.as_view(), name='health-check'),
    path("api/v1/", APIRootView.as_view(), name='api-root'),
    path("api/v1/", include("core.urls")),
    path("api/v1/shipments/domestic/", include("domestic.urls")),
    path("api/v1/shipments/", include("shipments.urls")),
    path("api/v1/payments/", include("payments.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/gov/", include("gov.urls")),
    path("api/v1/analytics/", include("analytics.urls")),
    path("api/v1/international/", include("international.urls")),
    path("api/v1/pricing/", include("billing.urls")),
]
