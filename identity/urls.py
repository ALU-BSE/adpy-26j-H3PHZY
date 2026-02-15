from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.IdentityRegisterView.as_view(), name='identity-register'),
]
