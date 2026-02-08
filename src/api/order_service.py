"""
Order Service - Create and manage orders for the profit circuit.

This is the entry point for the revenue loop:
Customer → Request → Order Created → Payment → Fulfillment
"""

import json
import time
import hashlib
from typing import Dict, Optional
from pathlib import Path

from audit_utils import AuditLogManager


class OrderService:
    """Handles order creation with idempotency and rate limiting."""
    
    def __init__(self, orders_log_path: str = "src/memory/orders.jsonl"):
        self.audit_log = AuditLogManager(orders_log_path)
        self.orders_log = self.audit_log.log_path  # Maintain backward compatibility

        # In-memory cache for idempotency (would use Redis in production)
        self.idempotency_cache = {}
        self.rate_limit_cache = {}
        
    def create_order(
        self,
        customer_id: str,
        service_type: str = "DATA_ANALYSIS_V1",
        amount: float = 50.00,
        payment_method: str = "sandbox",
        idempotency_key: Optional[str] = None,
        customer_ip: Optional[str] = None
    ) -> Dict:
        """
        Create a new order.
        
        Args:
            customer_id: Unique customer identifier
            service_type: SKU of the service (default: DATA_ANALYSIS_V1)
            amount: Price in USD (default: $50.00)
            payment_method: sandbox|cashapp|paypal
            idempotency_key: Prevents duplicate orders
            customer_ip: For rate limiting
            
        Returns:
            Order dict with order_id, status, payment_url
        """
        
        # 1. Rate limiting check (10 req/min per IP)
        if customer_ip:
            if not self._check_rate_limit(customer_ip):
                return {
                    "error": "rate_limit_exceeded",
                    "message": "Maximum 10 requests per minute",
                    "retry_after": 60
                }
        
        # 2. Idempotency check
        if idempotency_key:
            cached_order = self.idempotency_cache.get(idempotency_key)
            if cached_order:
                return cached_order  # Return same order, don't create duplicate
        
        # 3. Validate inputs
        if amount != 50.00:
            return {"error": "invalid_amount", "message": "Amount must be $50.00"}
        
        if service_type != "DATA_ANALYSIS_V1":
            return {"error": "invalid_service", "message": "Only DATA_ANALYSIS_V1 supported"}
        
        if payment_method not in ["sandbox", "cashapp", "paypal"]:
            return {"error": "invalid_payment_method", "message": "Must be sandbox, cashapp, or paypal"}
        
        # 4. Generate order
        timestamp = time.time()
        order_id = self._generate_order_id(customer_id, timestamp)
        
        order = {
            "order_id": order_id,
            "customer_id": customer_id,
            "service_type": service_type,
            "amount": amount,
            "payment_method": payment_method,
            "status": "pending_payment",
            "created_at": timestamp,
            "payment_url": self._generate_payment_url(order_id, amount, payment_method)
        }
        
        # 5. Log to audit trail
        self.audit_log.append_event({
            "timestamp": timestamp,
            "event_type": "order_created",
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "status": "pending_payment",
            "metadata": {
                "service_type": service_type,
                "payment_method": payment_method,
                "idempotency_key": idempotency_key
            }
        })
        
        # 6. Cache for idempotency
        if idempotency_key:
            self.idempotency_cache[idempotency_key] = order
        
        return order
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Retrieve order by ID from audit log."""
        # Get the first event for this order (order_created event)
        if not self.orders_log.exists():
            return None

        with open(self.orders_log, 'r') as f:
            for line in f:
                event = json.loads(line)
                if event.get('order_id') == order_id:
                    return event

        return None
    
    def _generate_order_id(self, customer_id: str, timestamp: float) -> str:
        """Generate unique order ID."""
        raw = f"{customer_id}{timestamp}{time.time()}"
        hash_val = hashlib.sha256(raw.encode()).hexdigest()[:12]
        return f"ord_{hash_val}"
    
    def _generate_payment_url(self, order_id: str, amount: float, method: str) -> str:
        """Generate payment URL based on method."""
        if method == "sandbox":
            return f"http://localhost:8000/api/v1/payments/confirm?order_id={order_id}&sandbox=true"
        elif method == "cashapp":
            return f"https://cash.app/$evez420/{amount}?note={order_id}"
        elif method == "paypal":
            return f"https://paypal.me/Rubikspubes69/{amount}"
        else:
            return ""
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Check if IP is within rate limit (10 req/min)."""
        now = time.time()
        
        if ip not in self.rate_limit_cache:
            self.rate_limit_cache[ip] = []
        
        # Clean old requests (older than 60 seconds)
        self.rate_limit_cache[ip] = [
            req_time for req_time in self.rate_limit_cache[ip]
            if now - req_time < 60
        ]
        
        # Check limit
        if len(self.rate_limit_cache[ip]) >= 10:
            return False
        
        # Add current request
        self.rate_limit_cache[ip].append(now)
        return True


# Simple Flask-like API (can replace with FastAPI/Flask later)
def create_order_endpoint(request_data: Dict) -> Dict:
    """API endpoint for creating orders."""
    service = OrderService()
    
    return service.create_order(
        customer_id=request_data.get('customer_id'),
        service_type=request_data.get('service_type', 'DATA_ANALYSIS_V1'),
        amount=request_data.get('amount', 50.00),
        payment_method=request_data.get('payment_method', 'sandbox'),
        idempotency_key=request_data.get('idempotency_key'),
        customer_ip=request_data.get('customer_ip')
    )


if __name__ == "__main__":
    # Test the service
    service = OrderService()
    
    print("Creating test order...")
    order = service.create_order(
        customer_id="test_customer_001",
        service_type="DATA_ANALYSIS_V1",
        amount=50.00,
        payment_method="sandbox",
        idempotency_key="test_key_001"
    )
    
    print(f"Order created: {json.dumps(order, indent=2)}")
    
    # Test idempotency
    print("\nTesting idempotency (should return same order)...")
    order2 = service.create_order(
        customer_id="test_customer_001",
        service_type="DATA_ANALYSIS_V1",
        amount=50.00,
        payment_method="sandbox",
        idempotency_key="test_key_001"
    )
    
    print(f"Same order returned: {order['order_id'] == order2['order_id']}")
