from django.urls import path
from . import views

urlpatterns = [
    path('routes/top/', views.TopRoutesView.as_view(), name='routes-top'),
    path('commodities/breakdown/', views.CommodityBreakdownView.as_view(), name='commodities-breakdown'),
    path('revenue/heatmap/', views.RevenueHeatmapView.as_view(), name='revenue-heatmap'),
    path('drivers/leaderboard/', views.DriverLeaderboardView.as_view(), name='drivers-leaderboard'),
]
