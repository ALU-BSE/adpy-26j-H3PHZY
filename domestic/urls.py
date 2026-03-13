from django.urls import path
from . import views

urlpatterns = [
    # Shipment management
    path('', views.ShipmentListCreateView.as_view(), name='shipment-list-create'),
    path('<str:tracking_number>/', views.ShipmentDetailView.as_view(), name='shipment-detail'),
    path('<str:tracking_number>/tracking/', views.ShipmentTrackingView.as_view(), name='shipment-tracking'),
    path('<str:tracking_number>/update-status/', views.ShipmentStatusUpdateView.as_view(), name='shipment-update-status'),
    path('batch-update/', views.ShipmentBatchUpdateView.as_view(), name='shipment-batch-update'),
]
