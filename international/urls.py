from django.urls import path
from . import views

urlpatterns = [
    # International shipments
    path('shipments/', views.InternationalShipmentListCreateView.as_view(), name='intl-shipment-list-create'),
    path('shipments/<str:tracking_number>/', views.InternationalShipmentDetailView.as_view(), name='intl-shipment-detail'),
    path('shipments/<str:tracking_number>/tracking/', views.InternationalShipmentTrackingView.as_view(), name='intl-shipment-tracking'),
]
