import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(name="notifications.send_shipment_notification")
def send_shipment_notification(recipient_phone, message, shipment_number, notification_type="SMS"):
    """
    Asynchronously send a shipment notification.
    In a real system, this would call an external API (Twilio, Africa's Talking, etc.)
    """
    logger.info(f"Sending {notification_type} to {recipient_phone} for shipment {shipment_number}: {message}")
    
    # Simulate processing time
    import time
    time.sleep(2)
    
    # In a more advanced version, we would create a log record in the notifications app
    # to track the history of messages sent.
    
    return {
        "status": "sent",
        "recipient": recipient_phone,
        "shipment": shipment_number,
        "timestamp": timezone.now().isoformat()
    }

@shared_task(name="notifications.process_batch_status_update")
def process_batch_status_update(updates, user_id):
    """
    Process a batch of status updates and send notifications for each.
    """
    from domestic.models import Shipment, ShipmentLog
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None

    processed_count = 0
    failed_count = 0
    
    for update in updates:
        tracking_number = update.get('tracking_number')
        new_status = update.get('status')
        notes = update.get('notes', '')
        
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
            old_status = shipment.status
            shipment.status = new_status
            shipment.save()
            
            # Log the change
            ShipmentLog.objects.create(
                shipment=shipment,
                status=new_status,
                notes=f"Batch update: {notes}",
                logged_by=user
            )
            
            # Trigger notification
            msg = f"Your shipment {tracking_number} status has changed from {old_status} to {new_status}."
            send_shipment_notification.delay(shipment.recipient_phone, msg, tracking_number)
            
            processed_count += 1
        except Exception as e:
            logger.error(f"Failed to update shipment {tracking_number}: {str(e)}")
            failed_count += 1
            
    return {
        "processed": processed_count,
        "failed": failed_count,
        "total": len(updates)
    }
