"""
Shared utilities for audit log operations.

This module centralizes common audit log functionality used across
OrderService, PaymentService, and FulfillmentService to eliminate code duplication.
"""

import json
from typing import Dict, Optional
from pathlib import Path


class AuditLogManager:
    """Manages audit log operations for order lifecycle events."""

    def __init__(self, log_path: str):
        """
        Initialize the audit log manager.

        Args:
            log_path: Path to the audit log file (JSONL format)
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append_event(self, event: Dict):
        """
        Append an event to the immutable audit log.

        Args:
            event: Event dictionary to log (will be serialized as JSON)
        """
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def get_order(self, order_id: str) -> Optional[Dict]:
        """
        Get the most recent order state from the audit log.

        This method reconstructs order state by replaying all events
        for the given order_id from the audit log.

        Args:
            order_id: The order ID to retrieve

        Returns:
            Order state dictionary with current status, or None if not found
        """
        if not self.log_path.exists():
            return None

        order_state = None
        with open(self.log_path, 'r') as f:
            for line in f:
                event = json.loads(line)
                if event.get('order_id') == order_id:
                    if not order_state:
                        # Initialize order state from first event
                        order_state = {
                            'order_id': order_id,
                            'customer_id': event.get('customer_id'),
                            'amount': event.get('amount'),
                            'status': event.get('status'),
                            'created_at': event.get('timestamp')
                        }
                    else:
                        # Update status from subsequent events
                        order_state['status'] = event.get('status', order_state['status'])

        return order_state
