from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.IdentityRegisterView.as_view(), name='identity-register'),
    path('request-otp/', views.RequestOTPView.as_view(), name='identity-request-otp'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='identity-verify-otp'),
]
