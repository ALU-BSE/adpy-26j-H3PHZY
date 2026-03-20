from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .tasks import send_shipment_notification
from core.models import User

class AdminBroadcastView(generics.GenericAPIView):
    """Admin alert to all drivers"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all users of type AGENT (drivers in this context)
        drivers = User.objects.filter(user_type='AGENT')
        
        for driver in drivers:
            if driver.phone:
                # Reuse the existing notification task
                send_shipment_notification.delay(
                    driver.phone, 
                    f"BROADCAST: {message}", 
                    "SYSTEM-ALERT",
                    "SMS"
                )
        
        return Response({
            'message': f'Broadcast sent to {drivers.count()} drivers',
            'status': 'success'
        })
