"""
Intent Token - Pre-action and post-event causal tracking

Captures the full lifecycle of an intent from goal formation through execution
and causal readout. Enables measurement and storage of:
- Pre-action: goal, constraints, success signals, confidence
- Post-event: trigger, state, default policy, payoff

Design Principles:
- Stored and measurable
- Links to events and hypotheses
- Auditable lifecycle tracking
"""

import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional


class IntentStatus(Enum):
    """Lifecycle status of an intent"""
    FORMING = "forming"  # Goal being defined
    READY = "ready"  # Pre-action complete, ready to execute
    EXECUTING = "executing"  # Currently executing
    COMPLETED = "completed"  # Execution complete, gathering readout
    ANALYZED = "analyzed"  # Post-event analysis complete
    FAILED = "failed"  # Execution failed
    CANCELLED = "cancelled"  # Intent cancelled before execution


@dataclass
class PreActionIntent:
    """
    Pre-action intent specification.
    
    Captures what we intend to do before doing it, including:
    - Goal: What we're trying to achieve
    - Constraints: Boundaries and requirements
    - Success signal: How we'll know if it worked
    - Confidence: How confident we are in this approach
    """
    
    # What are we trying to achieve?
    goal: str
    goal_details: Dict[str, Any] = field(default_factory=dict)
    
    # What are the constraints?
    constraints: List[str] = field(default_factory=list)
    constraint_details: Dict[str, Any] = field(default_factory=dict)
    
    # How will we know success?
    success_signals: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # How confident are we? (0.0 to 1.0)
    confidence: float = 0.5
    confidence_basis: Optional[str] = None
    
    # When was this intent formed?
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class PostEventCausal:
    """
    Post-event causal readout.
    
    After execution, captures:
    - Trigger: What initiated the action
    - State: Resulting system state
    - Default policy: What would have happened without intervention
    - Payoff: Actual outcome vs expected outcome
    """
    
    # What triggered the action?
    trigger: str
    trigger_details: Dict[str, Any] = field(default_factory=dict)
    
    # What is the resulting state?
    resulting_state: Dict[str, Any] = field(default_factory=dict)
    state_description: Optional[str] = None
    
    # What would default policy have done?
    default_policy_outcome: Optional[str] = None
    default_policy_details: Dict[str, Any] = field(default_factory=dict)
    
    # What was the actual payoff?
    payoff: float = 0.0  # Numeric payoff measure
    payoff_description: Optional[str] = None
    payoff_breakdown: Dict[str, Any] = field(default_factory=dict)
    
    # When was this readout captured?
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class IntentToken:
    """
    Complete intent token tracking pre-action and post-event causality.
    
    Lifecycle:
    1. Create with pre_action intent
    2. Execute action
    3. Capture post_event causal readout
    4. Link to events and hypotheses
    
    Fully stored and measurable for analysis.
    """
    
    # Core identifiers
    intent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    
    # Lifecycle tracking
    status: IntentStatus = IntentStatus.FORMING
    
    # Pre-action specification
    pre_action: Optional[PreActionIntent] = None
    
    # Post-event causal readout
    post_event: Optional[PostEventCausal] = None
    
    # Links to system objects
    related_events: List[str] = field(default_factory=list)
    related_hypotheses: List[str] = field(default_factory=list)
    parent_intent: Optional[str] = None  # For hierarchical intents
    child_intents: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def set_pre_action(
        self,
        goal: str,
        constraints: Optional[List[str]] = None,
        success_signals: Optional[List[str]] = None,
        confidence: float = 0.5,
        **kwargs
    ) -> None:
        """Set pre-action intent"""
        self.pre_action = PreActionIntent(
            goal=goal,
            constraints=constraints or [],
            success_signals=success_signals or [],
            confidence=confidence,
            **kwargs
        )
        self.status = IntentStatus.READY
    
    def start_execution(self) -> None:
        """Mark intent as executing"""
        if self.status != IntentStatus.READY:
            raise ValueError(f"Cannot execute intent in status {self.status}")
        self.status = IntentStatus.EXECUTING
    
    def set_post_event(
        self,
        trigger: str,
        resulting_state: Dict[str, Any],
        payoff: float,
        default_policy_outcome: Optional[str] = None,
        **kwargs
    ) -> None:
        """Set post-event causal readout"""
        self.post_event = PostEventCausal(
            trigger=trigger,
            resulting_state=resulting_state,
            payoff=payoff,
            default_policy_outcome=default_policy_outcome,
            **kwargs
        )
        self.status = IntentStatus.COMPLETED
    
    def mark_analyzed(self) -> None:
        """Mark post-event analysis as complete"""
        if self.status != IntentStatus.COMPLETED:
            raise ValueError(f"Cannot analyze intent in status {self.status}")
        self.status = IntentStatus.ANALYZED
    
    def mark_failed(self, reason: Optional[str] = None) -> None:
        """Mark intent as failed"""
        self.status = IntentStatus.FAILED
        if reason:
            self.metadata['failure_reason'] = reason
    
    def mark_cancelled(self, reason: Optional[str] = None) -> None:
        """Mark intent as cancelled"""
        self.status = IntentStatus.CANCELLED
        if reason:
            self.metadata['cancellation_reason'] = reason
    
    def calculate_success(self) -> Optional[bool]:
        """
        Calculate if intent was successful based on pre/post comparison.
        
        Returns:
            True if success criteria met, False if not, None if can't determine
        """
        if not self.pre_action or not self.post_event:
            return None
        
        # Simple heuristic: positive payoff and status is completed/analyzed
        if self.status in (IntentStatus.COMPLETED, IntentStatus.ANALYZED):
            return self.post_event.payoff > 0
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntentToken':
        """Create from dictionary"""
        # Handle IntentStatus enum
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = IntentStatus(data['status'])
        
        # Handle nested dataclasses
        if 'pre_action' in data and isinstance(data['pre_action'], dict):
            data['pre_action'] = PreActionIntent(**data['pre_action'])
        
        if 'post_event' in data and isinstance(data['post_event'], dict):
            data['post_event'] = PostEventCausal(**data['post_event'])
        
        return cls(**data)


class IntentRegistry:
    """
    Registry for tracking intent tokens.
    
    Provides storage, retrieval, and analysis of intent lifecycle.
    """
    
    def __init__(self):
        """Initialize intent registry"""
        self.intents: Dict[str, IntentToken] = {}
    
    def register(self, intent: IntentToken) -> None:
        """Register a new intent"""
        self.intents[intent.intent_id] = intent
    
    def get(self, intent_id: str) -> Optional[IntentToken]:
        """Get intent by ID"""
        return self.intents.get(intent_id)
    
    def query_by_status(self, status: IntentStatus) -> List[IntentToken]:
        """Query intents by status"""
        return [
            intent for intent in self.intents.values()
            if intent.status == status
        ]
    
    def get_success_rate(self) -> float:
        """Calculate overall success rate"""
        completed = [
            intent for intent in self.intents.values()
            if intent.status in (IntentStatus.COMPLETED, IntentStatus.ANALYZED)
        ]
        
        if not completed:
            return 0.0
        
        successes = sum(
            1 for intent in completed
            if intent.calculate_success() is True
        )
        
        return successes / len(completed)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get overall metrics"""
        total = len(self.intents)
        by_status = {}
        for status in IntentStatus:
            count = len(self.query_by_status(status))
            by_status[status.value] = count
        
        return {
            'total_intents': total,
            'by_status': by_status,
            'success_rate': self.get_success_rate()
        }
