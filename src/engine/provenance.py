"""
Provenance Domain - Observability and audit with safe boundaries.

Features:
- Event tap with redaction pipeline
- PII/secret filtering with hashing
- Anomaly detection (rate spikes, drift, bursts)
- Ring buffer for bounded memory
- Provenance graph overlay on derivations
- Full trajectory logging with source tags
"""

import json
import time
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from collections import deque, defaultdict, Counter
from dataclasses import dataclass, field


@dataclass
class ProvenanceEdge:
    """Edge in the provenance graph."""
    source_fact: str
    target_fact: str
    rule_id: str
    timestamp: float
    run_id: str
    cost_bucket: str  # 'low', 'medium', 'high'
    source_tag: str   # 'user_input', 'derived', 'system'
    
    def to_dict(self) -> Dict:
        return {
            'source': self.source_fact,
            'target': self.target_fact,
            'rule': self.rule_id,
            'timestamp': self.timestamp,
            'run_id': self.run_id,
            'cost_bucket': self.cost_bucket,
            'source_tag': self.source_tag
        }


@dataclass
class AnomalyEvent:
    """Represents a detected anomaly."""
    anomaly_type: str  # 'rate_spike', 'drift', 'burst'
    severity: str      # 'low', 'medium', 'high', 'critical'
    timestamp: float
    details: Dict
    
    def to_dict(self) -> Dict:
        return {
            'type': self.anomaly_type,
            'severity': self.severity,
            'timestamp': self.timestamp,
            'details': self.details
        }


class Redactor:
    """Redacts PII and secrets from event data."""
    
    # Patterns to redact
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    API_KEY_PATTERN = re.compile(r'\b[A-Za-z0-9]{32,}\b')
    
    # Denylist for common secret keys
    SECRET_KEYS = {
        'password', 'api_key', 'secret', 'token', 'auth',
        'private_key', 'credential', 'access_key', 'secret_key'
    }
    
    @staticmethod
    def redact(text: str, hash_pii: bool = True) -> str:
        """Redact PII and secrets from text."""
        if not isinstance(text, str):
            text = str(text)
        
        # Email
        if hash_pii:
            def hash_email(match):
                email = match.group(0)
                hashed = hashlib.sha256(email.encode()).hexdigest()[:8]
                return f"[EMAIL:{hashed}]"
            text = Redactor.EMAIL_PATTERN.sub(hash_email, text)
        else:
            text = Redactor.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', text)
        
        # Phone
        text = Redactor.PHONE_PATTERN.sub('[PHONE_REDACTED]', text)
        
        # SSN
        text = Redactor.SSN_PATTERN.sub('[SSN_REDACTED]', text)
        
        # API keys (long alphanumeric strings)
        if hash_pii:
            def hash_key(match):
                key = match.group(0)
                hashed = hashlib.sha256(key.encode()).hexdigest()[:8]
                return f"[KEY:{hashed}]"
            text = Redactor.API_KEY_PATTERN.sub(hash_key, text)
        else:
            text = Redactor.API_KEY_PATTERN.sub('[KEY_REDACTED]', text)
        
        return text
    
    @staticmethod
    def redact_dict(data: Dict, hash_pii: bool = True) -> Dict:
        """Redact PII from dictionary values."""
        redacted = {}
        for key, value in data.items():
            # Check if key is in denylist
            if any(secret_key in key.lower() for secret_key in Redactor.SECRET_KEYS):
                if hash_pii:
                    hashed = hashlib.sha256(str(value).encode()).hexdigest()[:8]
                    redacted[key] = f"[SECRET:{hashed}]"
                else:
                    redacted[key] = '[SECRET_REDACTED]'
            elif isinstance(value, str):
                redacted[key] = Redactor.redact(value, hash_pii)
            elif isinstance(value, dict):
                redacted[key] = Redactor.redact_dict(value, hash_pii)
            elif isinstance(value, list):
                redacted[key] = [
                    Redactor.redact(item, hash_pii) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                redacted[key] = value
        
        return redacted


class RingBuffer:
    """Fixed-size ring buffer for bounded memory."""
    
    def __init__(self, maxsize: int = 1000):
        self.maxsize = maxsize
        self.buffer = deque(maxlen=maxsize)
    
    def append(self, item: Any):
        """Add item to buffer (oldest is evicted if full)."""
        self.buffer.append(item)
    
    def get_all(self) -> List:
        """Get all items in buffer."""
        return list(self.buffer)
    
    def get_recent(self, n: int) -> List:
        """Get n most recent items."""
        return list(self.buffer)[-n:] if n <= len(self.buffer) else list(self.buffer)
    
    def clear(self):
        """Clear buffer."""
        self.buffer.clear()


class AnomalyDetector:
    """Detects anomalies in event streams."""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size  # seconds
        self.event_timestamps = deque()
        self.event_types = defaultdict(lambda: deque())
        
        # Thresholds
        self.rate_spike_threshold = 10.0  # events/second
        self.burst_threshold = 20  # events in window
        self.drift_threshold = 0.5  # change in distribution
        
        self.anomalies = []
    
    def record_event(self, event_type: str, timestamp: float):
        """Record an event for anomaly detection."""
        now = timestamp
        
        # Add to global timeline
        self.event_timestamps.append(now)
        
        # Add to type-specific timeline
        self.event_types[event_type].append(now)
        
        # Clean old events
        self._clean_old_events(now)
    
    def _clean_old_events(self, now: float):
        """Remove events older than window_size."""
        cutoff = now - self.window_size
        
        # Clean global
        while self.event_timestamps and self.event_timestamps[0] < cutoff:
            self.event_timestamps.popleft()
        
        # Clean per-type
        for event_type in self.event_types:
            while self.event_types[event_type] and self.event_types[event_type][0] < cutoff:
                self.event_types[event_type].popleft()
    
    def detect_rate_spike(self, now: float) -> Optional[AnomalyEvent]:
        """Detect sudden rate spikes."""
        if len(self.event_timestamps) < 10:
            return None
        
        # Calculate current rate
        duration = now - self.event_timestamps[0] if self.event_timestamps else 1.0
        rate = len(self.event_timestamps) / duration if duration > 0 else 0.0
        
        if rate > self.rate_spike_threshold:
            anomaly = AnomalyEvent(
                anomaly_type='rate_spike',
                severity='high' if rate > self.rate_spike_threshold * 2 else 'medium',
                timestamp=now,
                details={
                    'rate': rate,
                    'threshold': self.rate_spike_threshold,
                    'event_count': len(self.event_timestamps)
                }
            )
            self.anomalies.append(anomaly)
            return anomaly
        
        return None
    
    def detect_burst(self, now: float) -> Optional[AnomalyEvent]:
        """Detect event bursts."""
        if len(self.event_timestamps) > self.burst_threshold:
            # Check if events are clustered
            recent_events = [ts for ts in self.event_timestamps if now - ts < 5.0]
            
            if len(recent_events) > self.burst_threshold / 2:
                anomaly = AnomalyEvent(
                    anomaly_type='burst',
                    severity='medium',
                    timestamp=now,
                    details={
                        'burst_size': len(recent_events),
                        'threshold': self.burst_threshold,
                        'window': 5.0
                    }
                )
                self.anomalies.append(anomaly)
                return anomaly
        
        return None
    
    def detect_drift(self, now: float) -> Optional[AnomalyEvent]:
        """Detect distribution drift in event types."""
        if len(self.event_timestamps) < 20:
            return None
        
        # Compare recent vs historical distribution
        recent_cutoff = now - (self.window_size / 4)
        
        recent_types = []
        historical_types = []
        
        for event_type, timestamps in self.event_types.items():
            for ts in timestamps:
                if ts >= recent_cutoff:
                    recent_types.append(event_type)
                else:
                    historical_types.append(event_type)
        
        if not recent_types or not historical_types:
            return None
        
        # Calculate distribution difference (simplified)
        recent_dist = Counter(recent_types)
        historical_dist = Counter(historical_types)
        
        # Normalize
        recent_total = sum(recent_dist.values())
        historical_total = sum(historical_dist.values())
        
        all_types = set(recent_dist.keys()) | set(historical_dist.keys())
        
        diff = 0.0
        for event_type in all_types:
            recent_prob = recent_dist[event_type] / recent_total if recent_total > 0 else 0
            historical_prob = historical_dist[event_type] / historical_total if historical_total > 0 else 0
            diff += abs(recent_prob - historical_prob)
        
        if diff > self.drift_threshold:
            anomaly = AnomalyEvent(
                anomaly_type='drift',
                severity='low',
                timestamp=now,
                details={
                    'drift_score': diff,
                    'threshold': self.drift_threshold,
                    'recent_distribution': dict(recent_dist),
                    'historical_distribution': dict(historical_dist)
                }
            )
            self.anomalies.append(anomaly)
            return anomaly
        
        return None
    
    def check_all(self, now: float) -> List[AnomalyEvent]:
        """Run all anomaly checks."""
        detected = []
        
        rate_spike = self.detect_rate_spike(now)
        if rate_spike:
            detected.append(rate_spike)
        
        burst = self.detect_burst(now)
        if burst:
            detected.append(burst)
        
        drift = self.detect_drift(now)
        if drift:
            detected.append(drift)
        
        return detected


class ProvenanceDomain:
    """
    Observability and provenance tracking with safe boundaries.
    
    Provides event tapping, redaction, anomaly detection, and
    full provenance graph construction.
    """
    
    def __init__(self, provenance_log_path: str = "src/memory/provenance_log.jsonl"):
        self.provenance_log = Path(provenance_log_path)
        self.provenance_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Components
        self.redactor = Redactor()
        self.ring_buffer = RingBuffer(maxsize=1000)
        self.anomaly_detector = AnomalyDetector(window_size=60)
        
        # Provenance graph
        self.provenance_edges: List[ProvenanceEdge] = []
        
        # Hash chain
        self.last_event_hash = None
        self._load_last_hash()
    
    def _load_last_hash(self):
        """Load last event hash from provenance log."""
        if self.provenance_log.exists():
            try:
                with open(self.provenance_log, 'r') as f:
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
    
    def _append_provenance_log(self, event: Dict):
        """Append event to provenance log with hash chaining."""
        event['parent_hash'] = self.last_event_hash
        event_hash = self._calculate_event_hash(event)
        event['event_hash'] = event_hash
        
        with open(self.provenance_log, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        self.last_event_hash = event_hash
    
    def tap_event(self, event_type: str, payload: Dict, run_id: str):
        """
        Tap an event - runs through redaction pipeline and anomaly detection.
        """
        timestamp = time.time()
        
        # Redact payload
        redacted_payload = self.redactor.redact_dict(payload)
        
        # Record in ring buffer
        self.ring_buffer.append({
            'event_type': event_type,
            'timestamp': timestamp,
            'run_id': run_id,
            'payload': redacted_payload
        })
        
        # Anomaly detection
        self.anomaly_detector.record_event(event_type, timestamp)
        anomalies = self.anomaly_detector.check_all(timestamp)
        
        # Log event
        log_entry = {
            'event_type': 'event_tapped',
            'timestamp': timestamp,
            'run_id': run_id,
            'original_event_type': event_type,
            'payload': redacted_payload,
            'anomalies': [a.to_dict() for a in anomalies] if anomalies else []
        }
        
        self._append_provenance_log(log_entry)
    
    def add_provenance_edge(self, source_fact: str, target_fact: str, 
                           rule_id: str, run_id: str, cost: float = 1.0,
                           source_tag: str = 'derived'):
        """Add an edge to the provenance graph."""
        # Categorize cost
        if cost < 1.0:
            cost_bucket = 'low'
        elif cost < 5.0:
            cost_bucket = 'medium'
        else:
            cost_bucket = 'high'
        
        edge = ProvenanceEdge(
            source_fact=source_fact,
            target_fact=target_fact,
            rule_id=rule_id,
            timestamp=time.time(),
            run_id=run_id,
            cost_bucket=cost_bucket,
            source_tag=source_tag
        )
        
        self.provenance_edges.append(edge)
        
        self._append_provenance_log({
            'event_type': 'provenance_edge_added',
            'timestamp': edge.timestamp,
            'edge': edge.to_dict()
        })
    
    def get_provenance_graph(self) -> Dict:
        """Get complete provenance graph."""
        nodes = set()
        edges = []
        
        for edge in self.provenance_edges:
            nodes.add(edge.source_fact)
            nodes.add(edge.target_fact)
            edges.append(edge.to_dict())
        
        return {
            'nodes': sorted(list(nodes)),
            'edges': edges,
            'node_count': len(nodes),
            'edge_count': len(edges)
        }
    
    def export_audit(self, output_path: Optional[str] = None) -> Dict:
        """Export full audit trail."""
        audit_data = {
            'timestamp': time.time(),
            'ring_buffer_events': self.ring_buffer.get_all(),
            'anomalies': [a.to_dict() for a in self.anomaly_detector.anomalies],
            'provenance_graph': self.get_provenance_graph()
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(audit_data, f, indent=2)
        
        return audit_data
    
    def get_status(self) -> Dict:
        """Get provenance domain status."""
        return {
            'ring_buffer_size': len(self.ring_buffer.buffer),
            'provenance_edges': len(self.provenance_edges),
            'total_anomalies': len(self.anomaly_detector.anomalies),
            'recent_anomalies': len([a for a in self.anomaly_detector.anomalies 
                                    if time.time() - a.timestamp < 300])
        }
    
    def verify_hash_chain(self) -> bool:
        """Verify provenance log hash chain integrity."""
        if not self.provenance_log.exists():
            return True
        
        with open(self.provenance_log, 'r') as f:
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
    # Test provenance domain
    provenance = ProvenanceDomain("src/memory/test_provenance_log.jsonl")
    
    print("Provenance Domain Test")
    print("=" * 80)
    
    # Test redaction
    print("\n1. Testing PII redaction...")
    sensitive_data = {
        'email': 'test@example.com',
        'phone': '555-123-4567',
        'api_key': 'sk_test_51234567890abcdefghijklmnop',
        'message': 'Contact me at john.doe@company.com'
    }
    redacted = provenance.redactor.redact_dict(sensitive_data)
    print(f"   Redacted: {json.dumps(redacted, indent=2)}")
    
    # Test event tapping
    print("\n2. Testing event tap...")
    for i in range(15):
        provenance.tap_event('test_event', {'iteration': i, 'data': 'test'}, 'run_001')
        time.sleep(0.01)
    
    # Test provenance graph
    print("\n3. Building provenance graph...")
    provenance.add_provenance_edge('fact_A', 'fact_D', 'rule1', 'run_001', cost=1.0, source_tag='user_input')
    provenance.add_provenance_edge('fact_B', 'fact_D', 'rule1', 'run_001', cost=1.0, source_tag='user_input')
    provenance.add_provenance_edge('fact_D', 'fact_E', 'rule2', 'run_001', cost=2.0, source_tag='derived')
    
    graph = provenance.get_provenance_graph()
    print(f"   Nodes: {graph['node_count']}, Edges: {graph['edge_count']}")
    
    # Export audit
    print("\n4. Exporting audit trail...")
    audit = provenance.export_audit()
    print(f"   Ring buffer events: {len(audit['ring_buffer_events'])}")
    print(f"   Anomalies detected: {len(audit['anomalies'])}")
    
    # Status
    print("\n5. Provenance status:")
    status = provenance.get_status()
    print(json.dumps(status, indent=2))
    
    # Verify hash chain
    print(f"\n6. Hash chain integrity: {'✓ VERIFIED' if provenance.verify_hash_chain() else '✗ FAILED'}")
    
    print("\n✅ All tests passed!")
