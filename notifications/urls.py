from django.urls import path
from . import views

urlpatterns = [
    path('broadcast/', views.AdminBroadcastView.as_view(), name='admin-broadcast'),
]
