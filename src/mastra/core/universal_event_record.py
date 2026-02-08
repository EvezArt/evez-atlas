"""
Universal Event Record - HandshakeOS-E

Captures all state shifts, device/network routing, negotiation, social dynamics,
and model-to-user interaction with no single-domain bias.

Design Philosophy:
- Universal: Applies to all domains (technical, social, physical, abstract)
- Emergent: Domain signatures emerge from event patterns, not predetermined
- Attributed: Every event traces to a bounded identity
- Auditable: Complete audit trail for accountability
- Reversible: Events can be marked as reversible with undo procedures

For the stranger who wears your shell tomorrow:
This is the foundational event recording mechanism. All system activities
should create UniversalEventRecords. The domain_signature field captures
the emergent mixture of domains (e.g., 60% technical, 30% social, 10% financial)
rather than forcing events into single categories.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json
import math


@dataclass
class DomainSignature:
    """
    Emergent domain mixture vector - no single-domain bias.
    
    Domains emerge from patterns rather than being pre-assigned.
    Each event contributes to multiple domains with different weights.
    
    Attributes:
        technical: Weight for technical/computational aspects (0.0-1.0)
        social: Weight for social dynamics/interaction (0.0-1.0)
        financial: Weight for economic/transactional aspects (0.0-1.0)
        temporal: Weight for time-based/sequential aspects (0.0-1.0)
        spatial: Weight for location/routing aspects (0.0-1.0)
        cognitive: Weight for reasoning/decision aspects (0.0-1.0)
        
    Note: Weights don't have to sum to 1.0. Entropy measures mixture complexity.
    """
    technical: float = 0.0
    social: float = 0.0
    financial: float = 0.0
    temporal: float = 0.0
    spatial: float = 0.0
    cognitive: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary representation."""
        return {
            'technical': self.technical,
            'social': self.social,
            'financial': self.financial,
            'temporal': self.temporal,
            'spatial': self.spatial,
            'cognitive': self.cognitive,
        }
    
    def calculate_entropy(self) -> float:
        """
        Calculate Shannon entropy of domain mixture.
        Higher entropy = more mixed domains (less biased).
        
        Returns:
            float: Entropy value (0.0 = single domain, higher = more mixed)
        """
        weights = [
            self.technical, self.social, self.financial,
            self.temporal, self.spatial, self.cognitive
        ]
        
        # Normalize to probabilities
        total = sum(weights)
        if total == 0:
            return 0.0
        
        probs = [w / total for w in weights if w > 0]
        
        # Shannon entropy: H = -Σ(p * log2(p))
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        
        return entropy


@dataclass
class UniversalEventRecord:
    """
    Universal Event Record - captures all state shifts with domain-agnostic structure.
    
    This is the core event recording mechanism for HandshakeOS-E. Every significant
    action, state change, or interaction should create a UniversalEventRecord.
    
    Key Design Points:
    1. No single-domain bias: Events can span multiple domains
    2. Complete state tracking: Before, after, and delta
    3. Full attribution: Every event traces to a bounded identity
    4. Audit trail: Complete history of who did what when
    5. Reversibility: Events can be marked as reversible
    
    Example Usage:
        >>> from src.mastra.core import UniversalEventRecord, DomainSignature
        >>> 
        >>> # Record a user interaction
        >>> event = UniversalEventRecord(
        ...     event_type="user_query",
        ...     state_before={"query": None, "context": "idle"},
        ...     state_after={"query": "What is X?", "context": "processing"},
        ...     attributed_to="user_123",
        ...     domain_signature=DomainSignature(
        ...         technical=0.3,
        ...         social=0.5,
        ...         cognitive=0.7
        ...     )
        ... )
        >>> 
        >>> # Save to audit log
        >>> event.save_to_log("data/events.jsonl")
    """
    
    # Core identification
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = ""
    
    # State tracking - captures what changed
    state_before: Dict[str, Any] = field(default_factory=dict)
    state_after: Dict[str, Any] = field(default_factory=dict)
    state_delta: Dict[str, Any] = field(default_factory=dict)
    
    # Device & network routing
    device_id: Optional[str] = None
    network_route: List[str] = field(default_factory=list)
    negotiation_context: Optional[Dict[str, Any]] = None
    
    # Social dynamics & model interaction
    social_dynamics: Optional[Dict[str, Any]] = None
    model_interaction: Optional[Dict[str, Any]] = None
    
    # Domain mixture (no single-domain bias)
    domain_signature: DomainSignature = field(default_factory=DomainSignature)
    domain_entropy: float = 0.0
    
    # Attribution & audit
    attributed_to: str = ""  # Bounded identity ID
    reversible: bool = False
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Versioning & linking
    version: str = "1.0.0"
    parent_event_id: Optional[str] = None
    related_event_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization: compute state delta and domain entropy."""
        if not self.state_delta and self.state_before and self.state_after:
            self.state_delta = self._compute_state_delta()
        
        if self.domain_entropy == 0.0:
            self.domain_entropy = self.domain_signature.calculate_entropy()
    
    def _compute_state_delta(self) -> Dict[str, Any]:
        """
        Compute the difference between state_before and state_after.
        
        Returns:
            Dict containing changes: {'added': {...}, 'removed': {...}, 'changed': {...}}
        """
        delta = {
            'added': {},
            'removed': {},
            'changed': {}
        }
        
        # Find added and changed keys
        for key, after_val in self.state_after.items():
            if key not in self.state_before:
                delta['added'][key] = after_val
            elif self.state_before[key] != after_val:
                delta['changed'][key] = {
                    'from': self.state_before[key],
                    'to': after_val
                }
        
        # Find removed keys
        for key in self.state_before:
            if key not in self.state_after:
                delta['removed'][key] = self.state_before[key]
        
        return delta
    
    def add_audit_entry(self, action: str, actor: str, details: Optional[Dict] = None):
        """
        Add an entry to the audit log.
        
        Args:
            action: What action was taken (e.g., "created", "modified", "accessed")
            actor: Who took the action (bounded identity ID)
            details: Optional additional details
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'actor': actor,
            'details': details or {}
        }
        self.audit_log.append(entry)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dict representation of the event record
        """
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'state_before': self.state_before,
            'state_after': self.state_after,
            'state_delta': self.state_delta,
            'device_id': self.device_id,
            'network_route': self.network_route,
            'negotiation_context': self.negotiation_context,
            'social_dynamics': self.social_dynamics,
            'model_interaction': self.model_interaction,
            'domain_signature': self.domain_signature.to_dict(),
            'domain_entropy': self.domain_entropy,
            'attributed_to': self.attributed_to,
            'reversible': self.reversible,
            'audit_log': self.audit_log,
            'version': self.version,
            'parent_event_id': self.parent_event_id,
            'related_event_ids': self.related_event_ids,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniversalEventRecord':
        """
        Create UniversalEventRecord from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            UniversalEventRecord instance
        """
        # Parse timestamp
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Parse domain signature
        if isinstance(data.get('domain_signature'), dict):
            data['domain_signature'] = DomainSignature(**data['domain_signature'])
        
        return cls(**data)
    
    def save_to_log(self, log_path: str):
        """
        Append this event to a JSONL log file.
        
        Args:
            log_path: Path to JSONL log file
        """
        import os
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Append to log (JSONL format: one JSON object per line)
        with open(log_path, 'a') as f:
            json.dump(self.to_dict(), f)
            f.write('\n')
    
    @staticmethod
    def load_from_log(log_path: str) -> List['UniversalEventRecord']:
        """
        Load all events from a JSONL log file.
        
        Args:
            log_path: Path to JSONL log file
            
        Returns:
            List of UniversalEventRecord instances
        """
        events = []
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        events.append(UniversalEventRecord.from_dict(data))
        except FileNotFoundError:
            pass  # Return empty list if file doesn't exist
        
        return events
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"UniversalEventRecord("
            f"id={self.event_id[:8]}..., "
            f"type={self.event_type}, "
            f"by={self.attributed_to}, "
            f"entropy={self.domain_entropy:.2f})"
        )


# Convenience function for quick event creation
def create_event(event_type: str,
                 attributed_to: str,
                 state_before: Optional[Dict] = None,
                 state_after: Optional[Dict] = None,
                 **kwargs) -> UniversalEventRecord:
    """
    Convenience function for creating UniversalEventRecords.
    
    Args:
        event_type: Type of event
        attributed_to: Bounded identity ID of actor
        state_before: State before event
        state_after: State after event
        **kwargs: Additional fields
        
    Returns:
        UniversalEventRecord instance
        
    Example:
        >>> event = create_event(
        ...     "data_query",
        ...     "agent_001",
        ...     state_before={'results': []},
        ...     state_after={'results': [1, 2, 3]},
        ...     device_id="server_1"
        ... )
    """
    return UniversalEventRecord(
        event_type=event_type,
        attributed_to=attributed_to,
        state_before=state_before or {},
        state_after=state_after or {},
        **kwargs
    )


if __name__ == "__main__":
    # Demo: Create and save an event
    print("🎯 UniversalEventRecord Demo")
    print("=" * 50)
    
    # Create a sample event
    event = create_event(
        event_type="user_interaction",
        attributed_to="user_alice",
        state_before={
            "query": None,
            "session_state": "idle"
        },
        state_after={
            "query": "Explain quantum computing",
            "session_state": "processing"
        },
        device_id="browser_chrome",
        network_route=["client", "load_balancer", "api_server"],
        social_dynamics={
            "user_confidence": 0.8,
            "interaction_mode": "exploratory"
        },
        domain_signature=DomainSignature(
            technical=0.6,
            social=0.4,
            cognitive=0.8,
            temporal=0.2
        )
    )
    
    print(f"\n✅ Created: {event}")
    print(f"\n📊 Domain Entropy: {event.domain_entropy:.3f}")
    print(f"   (Higher = more domain mixture, less biased)")
    
    print(f"\n🔄 State Delta:")
    print(f"   Added: {list(event.state_delta['added'].keys())}")
    print(f"   Changed: {list(event.state_delta['changed'].keys())}")
    print(f"   Removed: {list(event.state_delta['removed'].keys())}")
    
    # Add audit entry
    event.add_audit_entry("created", "system", {"source": "demo"})
    print(f"\n📝 Audit Log Entries: {len(event.audit_log)}")
    
    # Save to log
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "events.jsonl")
        event.save_to_log(log_path)
        print(f"\n💾 Saved to: {log_path}")
        
        # Load back
        loaded = UniversalEventRecord.load_from_log(log_path)
        print(f"✅ Loaded {len(loaded)} event(s) from log")
        
        if loaded:
            print(f"\n🔍 Loaded Event: {loaded[0]}")
            print(f"   State Delta: {loaded[0].state_delta}")
    
    print("\n" + "=" * 50)
    print("✅ Demo complete!")
