"""
Base Service - Common functionality for all API services.

Provides shared functionality for:
- Audit log management
- Order state retrieval
- Error handling patterns
"""

import json
from typing import Dict, Optional
from pathlib import Path


class BaseService:
    """Base class for order/payment/fulfillment services."""
    
    def __init__(self, orders_log_path: str = "src/memory/orders.jsonl"):
        """
        Initialize the service with audit log path.
        
        Args:
            orders_log_path: Path to the orders audit log
        """
        self.orders_log = Path(orders_log_path)
        self.orders_log.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_order(self, order_id: str) -> Optional[Dict]:
        """
        Get most recent order state from audit log.
        
        Reconstructs order state by replaying events from the audit log.
        
        Args:
            order_id: The order ID to retrieve
            
        Returns:
            Dictionary with order state or None if not found
        """
        if not self.orders_log.exists():
            return None
        
        order_state = None
        with open(self.orders_log, 'r') as f:
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
                        # Update with latest status
                        order_state['status'] = event.get('status', order_state['status'])
        
        return order_state
    
    def _append_audit_log(self, event: Dict):
        """
        Append event to immutable audit log.
        
        All events are written in append-only mode for auditability.
        
        Args:
            event: Dictionary with event data (must include timestamp, event_type, order_id)
        """
        with open(self.orders_log, 'a') as f:
            f.write(json.dumps(event) + '\n')
