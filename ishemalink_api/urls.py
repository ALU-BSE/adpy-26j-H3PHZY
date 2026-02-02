from django.urls import path

from django.urls import path
from core.views import UserRegistrationView, NIDVerificationView

urlpatterns = [
    path('api/auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('api/auth/verify-nid/', NIDVerificationView.as_view(), name='verify-nid'),
]