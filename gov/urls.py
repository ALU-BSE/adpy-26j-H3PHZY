from django.urls import path
from . import views

urlpatterns = [
    path('ebm/sign-receipt/', views.EBMSignReceiptView.as_view(), name='ebm-sign'),
    path('rura/verify-license/<str:license_no>/', views.RURAVerifyLicenseView.as_view(), name='rura-verify'),
    path('customs/generate-manifest/', views.CustomsManifestView.as_view(), name='customs-manifest'),
    path('audit/access-log/', views.GovAuditLogView.as_view(), name='gov-audit-log'),
]
