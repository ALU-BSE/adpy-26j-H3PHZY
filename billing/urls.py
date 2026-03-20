from django.urls import path
from . import views

urlpatterns = [
    path('tariffs/', views.TariffListView.as_view(), name='tariff-list'),
    path('zones/', views.ZoneListView.as_view(), name='zone-list'),
    path('calculate/', views.PricingCalculateView.as_view(), name='pricing-calculate'),
    path('admin/cache/clear-tariffs/', views.CacheClearView.as_view(), name='cache-clear'),
]
