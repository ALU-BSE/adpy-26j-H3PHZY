import threading
import time
from typing import Callable, Dict

from django.utils import timezone


class MomoMockGateway:
    """Mock mobile money gateway to simulate MTN/Airtel callbacks."""

    def __init__(self):
        # store listeners for callbacks keyed by transaction id
        self._callbacks: Dict[str, Callable[[Dict], None]] = {}

    def initiate_payment(self, amount: float, phone: str, callback: Callable[[Dict], None]) -> str:
        """Simulate initiating a payment. Returns a transaction id and schedules callback."""
        tx_id = f"TX{int(time.time() * 1000)}"
        # register callback
        self._callbacks[tx_id] = callback
        # schedule asynchronous success/failure after short delay
        threading.Timer(2.0, self._simulate_webhook, args=(tx_id, True)).start()
        return tx_id

    def handle_webhook(self, tx_id: str, success: bool):
        """Direct API to trigger a webhook event manually (could be called by tests)."""
        if tx_id in self._callbacks:
            payload = {
                'transaction_id': tx_id,
                'timestamp': timezone.now().isoformat(),
                'status': 'SUCCESS' if success else 'FAILURE',
            }
            self._callbacks[tx_id](payload)
            # once delivered, remove listener
            del self._callbacks[tx_id]

    def _simulate_webhook(self, tx_id: str, success: bool):

        self.handle_webhook(tx_id, success)
