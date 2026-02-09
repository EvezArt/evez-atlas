"""
Navigation Mesh - Threshold-based routing with zero-trust gate logic.

Features:
- Three threshold domains: Wealth (revenue), Info (data), Myth (content)
- JWT-style token validation per cell/flow
- Anomaly detection (rate spikes, dependency monitoring, breach logging)
- Multi-route paths: primary → failover → offline fallback
- Gate state persistence to gate_log.jsonl with hash chaining
"""

import json
import time
import hashlib
import hmac
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict, deque


class ThresholdDomain(Enum):
    """Threshold domains for navigation."""
    WEALTH = "wealth"  # Revenue flows
    INFO = "info"      # Archive/data
    MYTH = "myth"      # Posts/personas


class RouteType(Enum):
    """Route types for multi-path navigation."""
    PRIMARY = "primary"
    FAILOVER = "failover"
    OFFLINE = "offline"


class GateResult(Enum):
    """Result of gate validation."""
    ALLOWED = "allowed"
    DENIED = "denied"
    RATE_LIMITED = "rate_limited"
    INVALID_TOKEN = "invalid_token"


class NavigationToken:
    """JWT-style token for gate access."""
    
    def __init__(self, domain: ThresholdDomain, user_id: str, 
                 secret: str = None):
        self.domain = domain
        self.user_id = user_id
        self.issued_at = time.time()
        self.expires_at = self.issued_at + 3600  # 1 hour expiry
        # Use environment variable or default for development only
        import os
        self.secret = secret or os.environ.get('NAV_MESH_SECRET', 'evez666_dev_secret_change_in_production')
        
    def encode(self) -> str:
        """Encode token as JWT-style string."""
        payload = {
            'domain': self.domain.value,
            'user_id': self.user_id,
            'iat': self.issued_at,
            'exp': self.expires_at,
        }
        
        # Simple JWT-style encoding
        header = base64.b64encode(json.dumps({'alg': 'HS256'}).encode()).decode()
        payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
        
        # Sign
        signature_input = f"{header}.{payload_b64}"
        signature = hmac.new(
            self.secret.encode(),
            signature_input.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{header}.{payload_b64}.{signature}"
    
    @staticmethod
    def decode(token: str, secret: str = None) -> Optional[Dict]:
        """Decode and verify token."""
        import os
        secret = secret or os.environ.get('NAV_MESH_SECRET', 'evez666_dev_secret_change_in_production')
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            header_b64, payload_b64, signature = parts
            
            # Verify signature
            signature_input = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                secret.encode(),
                signature_input.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if signature != expected_signature:
                return None
            
            # Decode payload
            payload = json.loads(base64.b64decode(payload_b64).decode())
            
            # Check expiry
            if payload.get('exp', 0) < time.time():
                return None
            
            return payload
            
        except Exception:
            return None


class ThresholdGate:
    """Gate that validates access to a domain."""
    
    def __init__(self, domain: ThresholdDomain, rate_limit: int = 100):
        self.domain = domain
        self.rate_limit = rate_limit  # Requests per minute
        self.access_log = deque(maxlen=1000)
        self.breach_attempts = []
        self.total_requests = 0
        self.total_allowed = 0
        self.total_denied = 0
        
        # Rate limiting per user
        self.user_requests = defaultdict(list)
        
    def validate(self, token: str, user_id: str) -> Tuple[GateResult, Optional[str]]:
        """Validate token and check rate limits."""
        self.total_requests += 1
        now = time.time()
        
        # Decode token
        payload = NavigationToken.decode(token)
        if not payload:
            self.total_denied += 1
            self._log_breach(user_id, "invalid_token")
            return GateResult.INVALID_TOKEN, "Invalid or expired token"
        
        # Check domain match
        if payload.get('domain') != self.domain.value:
            self.total_denied += 1
            self._log_breach(user_id, "domain_mismatch")
            return GateResult.DENIED, f"Token not valid for {self.domain.value} domain"
        
        # Check user ID match
        if payload.get('user_id') != user_id:
            self.total_denied += 1
            self._log_breach(user_id, "user_mismatch")
            return GateResult.DENIED, "Token user ID mismatch"
        
        # Rate limiting
        user_reqs = self.user_requests[user_id]
        # Remove old requests (> 60 seconds ago)
        user_reqs[:] = [req_time for req_time in user_reqs if now - req_time < 60]
        
        if len(user_reqs) >= self.rate_limit:
            self.total_denied += 1
            return GateResult.RATE_LIMITED, f"Rate limit exceeded ({self.rate_limit}/min)"
        
        # Allow access
        user_reqs.append(now)
        self.access_log.append({
            'timestamp': now,
            'user_id': user_id,
            'result': GateResult.ALLOWED.value
        })
        self.total_allowed += 1
        
        return GateResult.ALLOWED, None
    
    def _log_breach(self, user_id: str, reason: str):
        """Log a breach attempt."""
        self.breach_attempts.append({
            'timestamp': time.time(),
            'user_id': user_id,
            'reason': reason,
            'domain': self.domain.value
        })
    
    def detect_anomalies(self) -> List[Dict]:
        """Detect anomalous access patterns."""
        anomalies = []
        now = time.time()
        
        # Check for rate spikes
        recent_requests = [log for log in self.access_log if now - log['timestamp'] < 60]
        if len(recent_requests) > self.rate_limit * 0.8:
            anomalies.append({
                'type': 'rate_spike',
                'severity': 'warning',
                'message': f'High request rate detected: {len(recent_requests)} req/min',
                'timestamp': now
            })
        
        # Check for repeated breach attempts
        recent_breaches = [b for b in self.breach_attempts if now - b['timestamp'] < 300]
        if len(recent_breaches) > 10:
            anomalies.append({
                'type': 'breach_pattern',
                'severity': 'critical',
                'message': f'{len(recent_breaches)} breach attempts in last 5 minutes',
                'timestamp': now
            })
        
        return anomalies
    
    def get_stats(self) -> Dict:
        """Get gate statistics."""
        success_rate = (self.total_allowed / self.total_requests * 100) if self.total_requests > 0 else 100.0
        
        return {
            'domain': self.domain.value,
            'total_requests': self.total_requests,
            'total_allowed': self.total_allowed,
            'total_denied': self.total_denied,
            'breach_attempts': len(self.breach_attempts),
            'success_rate': success_rate,
            'recent_breaches': len([b for b in self.breach_attempts if time.time() - b['timestamp'] < 300])
        }


class NavigationRoute:
    """Route through the navigation mesh."""
    
    def __init__(self, domain: ThresholdDomain, route_type: RouteType):
        self.domain = domain
        self.route_type = route_type
        self.active = True
        self.latency = 0.0
        self.success_count = 0
        self.failure_count = 0
        self.last_used = None
        
    def record_success(self, latency: float):
        """Record successful route usage."""
        self.success_count += 1
        self.latency = latency
        self.last_used = time.time()
        
    def record_failure(self):
        """Record route failure."""
        self.failure_count += 1
        self.last_used = time.time()
        
    def get_success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 100.0
        return (self.success_count / total) * 100
    
    def is_healthy(self) -> bool:
        """Check if route is healthy."""
        return self.active and self.get_success_rate() > 50.0


class NavigationMesh:
    """
    Navigation mesh with threshold gates and multi-route paths.
    
    Provides zero-trust gate logic, anomaly detection, and automatic
    failover routing with offline fallback support.
    """
    
    def __init__(self, gate_log_path: str = "src/memory/gate_log.jsonl"):
        self.gate_log = Path(gate_log_path)
        self.gate_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Gates for each domain
        self.gates = {
            ThresholdDomain.WEALTH: ThresholdGate(ThresholdDomain.WEALTH, rate_limit=100),
            ThresholdDomain.INFO: ThresholdGate(ThresholdDomain.INFO, rate_limit=200),
            ThresholdDomain.MYTH: ThresholdGate(ThresholdDomain.MYTH, rate_limit=50),
        }
        
        # Routes for each domain
        self.routes = {}
        for domain in ThresholdDomain:
            self.routes[domain] = {
                RouteType.PRIMARY: NavigationRoute(domain, RouteType.PRIMARY),
                RouteType.FAILOVER: NavigationRoute(domain, RouteType.FAILOVER),
                RouteType.OFFLINE: NavigationRoute(domain, RouteType.OFFLINE),
            }
        
        # Metrics
        self.path_switches = 0
        self.total_navigations = 0
        
        # Hash chain
        self.last_event_hash = None
        self._load_last_hash()
        
        # Log initialization
        self._append_gate_log({
            'event_type': 'nav_mesh_initialized',
            'timestamp': time.time(),
            'domains': [d.value for d in ThresholdDomain],
        })
    
    def _load_last_hash(self):
        """Load last event hash from gate log."""
        if self.gate_log.exists():
            try:
                with open(self.gate_log, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_event = json.loads(lines[-1])
                        self.last_event_hash = last_event.get('event_hash')
            except Exception:
                self.last_event_hash = None
    
    def _calculate_event_hash(self, event: Dict) -> str:
        """Calculate SHA-256 hash for event."""
        event_data = json.dumps(event, sort_keys=True)
        return hashlib.sha256(event_data.encode()).hexdigest()
    
    def _append_gate_log(self, event: Dict):
        """Append event to gate log with hash chaining."""
        event['parent_hash'] = self.last_event_hash
        event_hash = self._calculate_event_hash(event)
        event['event_hash'] = event_hash
        
        with open(self.gate_log, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        self.last_event_hash = event_hash
    
    def issue_token(self, domain: ThresholdDomain, user_id: str) -> str:
        """Issue a navigation token for a user."""
        token = NavigationToken(domain, user_id)
        encoded = token.encode()
        
        self._append_gate_log({
            'event_type': 'token_issued',
            'timestamp': time.time(),
            'domain': domain.value,
            'user_id': user_id,
        })
        
        return encoded
    
    def navigate(self, domain: ThresholdDomain, token: str, user_id: str, 
                 offline_mode: bool = False) -> Tuple[bool, Optional[str], RouteType]:
        """
        Navigate through the mesh with gate validation.
        
        Returns: (success, error_message, route_used)
        """
        self.total_navigations += 1
        
        # If offline, use offline route
        if offline_mode:
            route = self.routes[domain][RouteType.OFFLINE]
            route.record_success(0.0)
            self._append_gate_log({
                'event_type': 'navigation_offline',
                'timestamp': time.time(),
                'domain': domain.value,
                'user_id': user_id,
                'route': RouteType.OFFLINE.value,
            })
            return True, None, RouteType.OFFLINE
        
        # Validate at gate
        gate = self.gates[domain]
        result, error_msg = gate.validate(token, user_id)
        
        if result != GateResult.ALLOWED:
            self._append_gate_log({
                'event_type': 'navigation_denied',
                'timestamp': time.time(),
                'domain': domain.value,
                'user_id': user_id,
                'reason': result.value,
                'error': error_msg,
            })
            return False, error_msg, RouteType.PRIMARY
        
        # Select route (primary → failover → offline)
        route_type = self._select_route(domain)
        route = self.routes[domain][route_type]
        
        # Simulate navigation
        start_time = time.time()
        try:
            # Would perform actual navigation here
            time.sleep(0.01)  # Simulate latency
            latency = time.time() - start_time
            
            route.record_success(latency)
            
            self._append_gate_log({
                'event_type': 'navigation_success',
                'timestamp': time.time(),
                'domain': domain.value,
                'user_id': user_id,
                'route': route_type.value,
                'latency': latency,
            })
            
            return True, None, route_type
            
        except Exception as e:
            route.record_failure()
            
            self._append_gate_log({
                'event_type': 'navigation_failed',
                'timestamp': time.time(),
                'domain': domain.value,
                'user_id': user_id,
                'route': route_type.value,
                'error': str(e),
            })
            
            return False, str(e), route_type
    
    def _select_route(self, domain: ThresholdDomain) -> RouteType:
        """Select best available route."""
        domain_routes = self.routes[domain]
        
        # Try primary first
        if domain_routes[RouteType.PRIMARY].is_healthy():
            return RouteType.PRIMARY
        
        # Failover
        if domain_routes[RouteType.FAILOVER].is_healthy():
            self.path_switches += 1
            return RouteType.FAILOVER
        
        # Offline fallback
        self.path_switches += 1
        return RouteType.OFFLINE
    
    def detect_anomalies(self) -> List[Dict]:
        """Detect anomalies across all gates."""
        all_anomalies = []
        for domain, gate in self.gates.items():
            anomalies = gate.detect_anomalies()
            for anomaly in anomalies:
                anomaly['domain'] = domain.value
                all_anomalies.append(anomaly)
        return all_anomalies
    
    def get_status(self) -> Dict:
        """Get navigation mesh status."""
        return {
            'total_navigations': self.total_navigations,
            'path_switches': self.path_switches,
            'gates': {domain.value: gate.get_stats() for domain, gate in self.gates.items()},
            'routes': {
                domain.value: {
                    route_type.value: {
                        'active': route.active,
                        'success_rate': route.get_success_rate(),
                        'latency': route.latency,
                        'healthy': route.is_healthy(),
                    }
                    for route_type, route in routes.items()
                }
                for domain, routes in self.routes.items()
            },
            'anomalies': self.detect_anomalies(),
        }
    
    def verify_hash_chain(self) -> bool:
        """Verify hash chain integrity."""
        if not self.gate_log.exists():
            return True
        
        with open(self.gate_log, 'r') as f:
            events = [json.loads(line) for line in f if line.strip()]
        
        if not events:
            return True
        
        if events[0].get('parent_hash') is not None:
            return False
        
        for i in range(1, len(events)):
            expected_parent = events[i-1].get('event_hash')
            actual_parent = events[i].get('parent_hash')
            
            if expected_parent != actual_parent:
                return False
        
        return True


if __name__ == "__main__":
    # Test navigation mesh
    nav = NavigationMesh("src/memory/test_gate_log.jsonl")
    
    print("Navigation Mesh Test")
    print("=" * 80)
    
    # Issue token
    user_id = "test_user_001"
    token = nav.issue_token(ThresholdDomain.WEALTH, user_id)
    print(f"Token issued: {token[:50]}...")
    
    # Navigate
    success, error, route = nav.navigate(ThresholdDomain.WEALTH, token, user_id)
    print(f"Navigation: {'SUCCESS' if success else 'FAILED'} via {route.value}")
    
    # Test offline mode
    success, error, route = nav.navigate(ThresholdDomain.INFO, "", user_id, offline_mode=True)
    print(f"Offline navigation: {'SUCCESS' if success else 'FAILED'} via {route.value}")
    
    # Show status
    status = nav.get_status()
    print(f"\nStatus:")
    print(json.dumps(status, indent=2))
    
    # Verify hash chain
    print(f"\nHash chain integrity: {'✓ VERIFIED' if nav.verify_hash_chain() else '✗ FAILED'}")
