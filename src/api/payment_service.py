"""
Payment Service - Confirm payments and trigger fulfillment.

This bridges payment confirmation to order fulfillment:
Payment Received → Verify → Mark Paid → Trigger Fulfillment
"""

import json
import time
from typing import Dict, Optional
from pathlib import Path

from audit_utils import AuditLogManager


class PaymentService:
    """Handles payment confirmation and order updates."""
    
    def __init__(self, orders_log_path: str = "src/memory/orders.jsonl"):
        self.audit_log = AuditLogManager(orders_log_path)
        self.orders_log = self.audit_log.log_path  # Maintain backward compatibility
        
    def confirm_payment(
        self,
        order_id: str,
        payment_proof: Optional[str] = None,
        sandbox: bool = False
    ) -> Dict:
        """
        Confirm payment for an order.
        
        Args:
            order_id: The order to confirm payment for
            payment_proof: Transaction ID or proof (not needed for sandbox)
            sandbox: If True, auto-confirm for testing
            
        Returns:
            Payment confirmation dict with status
        """

        # 1. Get order details
        order = self.audit_log.get_order(order_id)
        if not order:
            return {"error": "order_not_found", "message": f"Order {order_id} not found"}
        
        # 2. Check if already paid
        if order.get('status') in ['paid', 'fulfilled', 'refunded']:
            return {
                "error": "already_processed",
                "message": f"Order already {order['status']}",
                "order_id": order_id,
                "status": order['status']
            }
        
        # 3. Verify payment (sandbox mode auto-confirms)
        if sandbox:
            payment_valid = True
            payment_proof = f"sandbox_payment_{time.time()}"
        else:
            # In production, verify with payment processor
            payment_valid = self._verify_payment_proof(order, payment_proof)
        
        if not payment_valid:
            return {
                "error": "payment_verification_failed",
                "message": "Could not verify payment",
                "order_id": order_id
            }
        
        # 4. Mark order as paid
        timestamp = time.time()
        self.audit_log.append_event({
            "timestamp": timestamp,
            "event_type": "payment_confirmed",
            "order_id": order_id,
            "customer_id": order.get('customer_id'),
            "amount": order.get('amount'),
            "status": "paid",
            "metadata": {
                "payment_proof": payment_proof,
                "sandbox": sandbox
            }
        })
        
        # 5. Return confirmation
        return {
            "success": True,
            "order_id": order_id,
            "status": "paid",
            "amount": order.get('amount'),
            "payment_proof": payment_proof,
            "confirmed_at": timestamp,
            "next_step": "fulfillment_triggered"
        }

    def _verify_payment_proof(self, order: Dict, payment_proof: Optional[str]) -> bool:
        """Verify payment proof (stub for production integration)."""
        # In production, this would:
        # 1. Call payment processor API (CashApp, PayPal, Stripe, etc.)
        # 2. Verify transaction ID matches order amount
        # 3. Confirm payment not already used
        # 4. Check payment not reversed/disputed
        
        if not payment_proof:
            return False

        # For now, basic validation
        return len(payment_proof) > 10


def confirm_payment_endpoint(request_data: Dict) -> Dict:
    """API endpoint for confirming payments."""
    service = PaymentService()
    
    return service.confirm_payment(
        order_id=request_data.get('order_id'),
        payment_proof=request_data.get('payment_proof'),
        sandbox=request_data.get('sandbox', False)
    )


if __name__ == "__main__":
    # Test the service
    from order_service import OrderService
    
    # Create an order first
    order_service = OrderService()
    print("Creating test order...")
    order = order_service.create_order(
        customer_id="test_customer_002",
        service_type="DATA_ANALYSIS_V1",
        amount=50.00,
        payment_method="sandbox",
        idempotency_key="test_payment_001"
    )
    
    print(f"Order created: {order['order_id']}")
    print(f"Payment URL: {order['payment_url']}")
    
    # Confirm payment
    payment_service = PaymentService()
    print("\nConfirming payment (sandbox mode)...")
    result = payment_service.confirm_payment(
        order_id=order['order_id'],
        sandbox=True
    )
    
    print(f"Payment confirmed: {json.dumps(result, indent=2)}")
    
    # Try to pay again (should fail)
    print("\nTrying to pay again (should fail)...")
    result2 = payment_service.confirm_payment(
        order_id=order['order_id'],
        sandbox=True
    )
    
    print(f"Second payment result: {json.dumps(result2, indent=2)}")
