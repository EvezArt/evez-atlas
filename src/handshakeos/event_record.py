"""
Universal Event Record - Domain-agnostic event tracking

Represents any event that happens in the system without forcing a single
domain interpretation. Events can represent internal state, routing,
negotiation, social dynamics, model-to-user interaction, or any mixture.

Key Features:
- No mandatory single-domain labels
- Domain mixture vectors can be empty/unknown and refined later
- All knowability comes from user input, device logs, or explicit tests
- Auditable, attributable, reversible (full logging and versioning)
"""

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional


class EventSource(Enum):
    """Source of event knowability"""
    USER_INPUT = "user_input"
    DEVICE_LOG = "device_log"
    USER_TEST = "user_test"
    SYSTEM_OBSERVATION = "system_observation"
    UNKNOWN = "unknown"


@dataclass
class DomainMixtureVector:
    """
    Domain-signature mixture vector for an event.
    
    Can be empty/unknown and refined later as more information becomes available.
    No single domain is required - events can exist in multiple domains simultaneously.
    """
    
    # Domain weights (all optional, can be None or 0.0)
    internal_state: Optional[float] = None
    routing: Optional[float] = None
    negotiation: Optional[float] = None
    social_dynamics: Optional[float] = None
    model_interaction: Optional[float] = None
    
    # Custom domain weights for extensibility
    custom_domains: Dict[str, float] = field(default_factory=dict)
    
    # Confidence in this mixture assessment (0.0 to 1.0)
    confidence: float = 0.0
    
    def is_empty(self) -> bool:
        """Check if the domain mixture is empty/unknown"""
        standard_domains = [
            self.internal_state,
            self.routing,
            self.negotiation,
            self.social_dynamics,
            self.model_interaction
        ]
        return (
            all(d is None or d == 0.0 for d in standard_domains) and
            not self.custom_domains
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class UniversalEventRecord:
    """
    Universal event record representing any system event without domain constraints.
    
    Design Principles:
    - Universal: Can represent any type of event
    - Domain-agnostic: No forced categorization
    - Auditable: Full logging with timestamps and IDs
    - Attributable: Clear source tracking
    - Reversible: Immutable records allow reconstruction
    """
    
    # Core identifiers
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    
    # Event content (flexible, domain-agnostic)
    event_type: str = "generic"
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Source of knowability
    source: EventSource = EventSource.UNKNOWN
    source_details: Optional[str] = None
    
    # Domain mixture (optional, can be refined later)
    domain_mixture: Optional[DomainMixtureVector] = None
    
    # Links to other system objects
    related_events: List[str] = field(default_factory=list)
    related_intents: List[str] = field(default_factory=list)
    related_hypotheses: List[str] = field(default_factory=list)
    
    # Versioning for reversibility
    version: int = 1
    supersedes: Optional[str] = None  # ID of event this refines/replaces
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['source'] = self.source.value
        if self.domain_mixture:
            data['domain_mixture'] = self.domain_mixture.to_dict()
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string (single line for JSONL format)"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniversalEventRecord':
        """Create from dictionary"""
        # Handle EventSource enum
        if 'source' in data and isinstance(data['source'], str):
            data['source'] = EventSource(data['source'])
        
        # Handle DomainMixtureVector
        if 'domain_mixture' in data and isinstance(data['domain_mixture'], dict):
            dmv_data = data['domain_mixture']
            # Extract custom_domains if present
            custom = dmv_data.pop('custom_domains', {})
            data['domain_mixture'] = DomainMixtureVector(
                custom_domains=custom,
                **{k: v for k, v in dmv_data.items() if k != 'custom_domains'}
            )
        
        return cls(**data)
    
    def refine_domain_mixture(self, new_mixture: DomainMixtureVector) -> 'UniversalEventRecord':
        """
        Create a new version with refined domain mixture.
        
        Returns a new event record that supersedes this one, maintaining
        auditability and reversibility.
        """
        new_event = UniversalEventRecord(
            event_id=str(uuid.uuid4()),
            timestamp=time.time(),
            event_type=self.event_type,
            payload=self.payload.copy(),
            source=self.source,
            source_details=self.source_details,
            domain_mixture=new_mixture,
            related_events=self.related_events.copy(),
            related_intents=self.related_intents.copy(),
            related_hypotheses=self.related_hypotheses.copy(),
            version=self.version + 1,
            supersedes=self.event_id,
            metadata=self.metadata.copy()
        )
        return new_event


class EventLog:
    """
    Append-only event log for HandshakeOS-E nervous system.
    
    Implements auditable, attributable, reversible patterns:
    - Append-only (no deletions)
    - Full versioning
    - Complete audit trail
    """
    
    def __init__(self, log_path: Optional[Path] = None):
        """
        Initialize event log.
        
        Args:
            log_path: Path to event log file (defaults to data/handshakeos_events.jsonl)
        """
        if log_path is None:
            base_dir = Path(__file__).resolve().parents[2]
            log_path = base_dir / "data" / "handshakeos_events.jsonl"
        
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def append(self, event: UniversalEventRecord) -> None:
        """Append event to log (immutable, append-only)"""
        with open(self.log_path, 'a') as f:
            f.write(event.to_json() + '\n')
    
    def read_all(self) -> List[UniversalEventRecord]:
        """Read all events from log"""
        if not self.log_path.exists():
            return []
        
        events = []
        with open(self.log_path, 'r') as f:
            for line in f:
                if line.strip():
                    events.append(
                        UniversalEventRecord.from_dict(json.loads(line))
                    )
        return events
    
    def query(
        self,
        event_type: Optional[str] = None,
        source: Optional[EventSource] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[UniversalEventRecord]:
        """Query events with filters"""
        events = self.read_all()
        
        filtered = []
        for event in events:
            if event_type and event.event_type != event_type:
                continue
            if source and event.source != source:
                continue
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            filtered.append(event)
        
        return filtered
