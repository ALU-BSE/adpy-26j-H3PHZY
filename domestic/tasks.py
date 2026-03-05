from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Shipment, ShipmentLog

User = get_user_model()


@shared_task
def process_batch_updates(updates, user_id=None):
    """Apply a list of shipment updates asynchronously.

    Each update should be a dict with keys `tracking_number`, optional
    `status` and `notes`.  The `user_id` is used to link the log entry
    back to the user who triggered the request (it may be None).
    """
    processed = 0
    failed = 0
    user = None
    if user_id is not None:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None

    for upd in updates:
        try:
            shipment = Shipment.objects.get(tracking_number=upd['tracking_number'])
            shipment.status = upd.get('status', shipment.status)
            shipment.save()

            ShipmentLog.objects.create(
                shipment=shipment,
                status=shipment.status,
                notes=upd.get('notes', ''),
                logged_by=user
            )
            processed += 1
        except Exception:
            failed += 1
    return {'processed': processed, 'failed': failed, 'total': len(updates)}
