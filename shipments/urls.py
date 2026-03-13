from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.ShipmentCreateView.as_view(), name='shipment-create'),
    path('<str:tracking_code>/live/', views.TrackingLiveView.as_view(), name='tracking-live'),
]
