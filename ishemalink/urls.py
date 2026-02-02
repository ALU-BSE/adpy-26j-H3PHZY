from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import HealthCheckView, APIRootView

router = DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Health and status
    path("api/status/", HealthCheckView.as_view(), name='health-check'),
    path("api/", APIRootView.as_view(), name='api-root'),
    
    # API endpoints
    path("api/", include("core.urls")),
    path("api/shipments/", include("domestic.urls")),
    path("api/international/", include("international.urls")),
    path("api/pricing/", include("billing.urls")),
]
