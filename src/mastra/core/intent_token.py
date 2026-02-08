"""
Intent Token - HandshakeOS-E

Tracks intent before and after action execution with comprehensive measurement
and audit trails.

Design Philosophy:
- Pre-action: Capture goal, constraints, success criteria, confidence before acting
- Post-action: Record trigger, final state, policy used, and measured payoff
- Direct measurement: Quantify outcomes objectively
- Complete audit: Every intent action fully traceable
- Linkage: Connect to events and hypotheses for full context

For the stranger who wears your shell tomorrow:
IntentTokens represent "actions with goals". Before executing, we record what
we're trying to achieve (pre-action). After executing, we record what actually
happened (post-action). This enables learning from the gap between intent and outcome.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json


@dataclass
class PreAction:
    """
    Pre-action fields: What we intend to do and how we'll measure success.
    
    Captured BEFORE action execution to establish intent and expectations.
    
    Attributes:
        goal: What we're trying to achieve (clear statement)
        constraints: Hard constraints that must be satisfied
        success_criteria: How we'll know if we succeeded
        confidence: How confident we are this will work (0.0-1.0)
    """
    goal: str = ""
    constraints: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    confidence: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'goal': self.goal,
            'constraints': self.constraints,
            'success_criteria': self.success_criteria,
            'confidence': self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PreAction':
        """Create PreAction from dictionary."""
        return cls(**data)


@dataclass
class PostAction:
    """
    Post-action fields: What actually happened and measured outcomes.
    
    Captured AFTER action execution to record reality vs. expectations.
    
    Attributes:
        trigger: What caused this action to execute
        final_state: Resulting state after action
        default_policy: Which fallback policy was used (if any)
        payoff: Measured outcome value (quantified benefit/cost)
    """
    trigger: str = ""
    final_state: Dict[str, Any] = field(default_factory=dict)
    default_policy: Optional[str] = None
    payoff: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'trigger': self.trigger,
            'final_state': self.final_state,
            'default_policy': self.default_policy,
            'payoff': self.payoff,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PostAction':
        """Create PostAction from dictionary."""
        return cls(**data)


@dataclass
class IntentToken:
    """
    IntentToken - captures goal-directed actions with pre/post tracking.
    
    Every goal-directed action should create an IntentToken. This enables:
    1. Understanding WHY actions are taken (goal)
    2. Setting clear success criteria upfront
    3. Measuring actual outcomes objectively (payoff)
    4. Learning from intent-outcome gaps
    5. Complete audit trail of decision-making
    
    Workflow:
        1. Create IntentToken with pre_action filled out
        2. Execute the action
        3. Fill out post_action with results
        4. Add measurements
        5. Save to audit log
    
    Example Usage:
        >>> from src.mastra.core import IntentToken, PreAction, PostAction
        >>> 
        >>> # Before action
        >>> intent = IntentToken(
        ...     pre_action=PreAction(
        ...         goal="Fetch user preferences",
        ...         constraints=["Must be under 100ms", "Use cached data if available"],
        ...         success_criteria=["Got preferences", "Response < 100ms"],
        ...         confidence=0.85
        ...     ),
        ...     attributed_to="agent_retriever"
        ... )
        >>> 
        >>> # Execute action
        >>> result = fetch_preferences()
        >>> 
        >>> # After action
        >>> intent.post_action = PostAction(
        ...     trigger="user_request",
        ...     final_state={"preferences": result, "latency_ms": 45},
        ...     payoff=0.9  # High success
        ... )
        >>> intent.add_measurement("latency_ms", 45)
        >>> intent.save_to_log("data/intents.jsonl")
    """
    
    # Core identification
    token_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Pre-action: BEFORE execution
    pre_action: PreAction = field(default_factory=PreAction)
    
    # Post-action: AFTER execution (optional until action completes)
    post_action: Optional[PostAction] = None
    completed_at: Optional[datetime] = None
    
    # Measurement & audit
    measurements: List[Dict[str, Any]] = field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    
    # Attribution (bounded identity)
    attributed_to: str = ""
    bounded_identity: Dict[str, Any] = field(default_factory=dict)
    
    # Linking to other HandshakeOS-E objects
    related_events: List[str] = field(default_factory=list)  # UniversalEventRecord IDs
    related_hypotheses: List[str] = field(default_factory=list)  # ParallelHypotheses IDs
    
    # Versioning
    version: str = "1.0.0"
    
    def complete(self,
                 trigger: str,
                 final_state: Dict[str, Any],
                 payoff: float,
                 default_policy: Optional[str] = None):
        """
        Complete the intent by recording post-action results.
        
        Args:
            trigger: What caused this action to execute
            final_state: Resulting state after action
            payoff: Measured outcome value
            default_policy: Which fallback policy was used (if any)
        """
        self.post_action = PostAction(
            trigger=trigger,
            final_state=final_state,
            default_policy=default_policy,
            payoff=payoff
        )
        self.completed_at = datetime.utcnow()
        
        # Add audit entry
        self.add_audit_entry("completed", self.attributed_to, {
            'payoff': payoff,
            'trigger': trigger
        })
    
    def add_measurement(self, metric: str, value: Any, unit: Optional[str] = None):
        """
        Add a direct measurement.
        
        Args:
            metric: Name of the metric being measured
            value: Measured value
            unit: Optional unit of measurement
        """
        measurement = {
            'timestamp': datetime.utcnow().isoformat(),
            'metric': metric,
            'value': value,
            'unit': unit
        }
        self.measurements.append(measurement)
    
    def add_audit_entry(self, action: str, actor: str, details: Optional[Dict] = None):
        """
        Add an entry to the audit log.
        
        Args:
            action: What action was taken
            actor: Who took the action
            details: Optional additional details
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'actor': actor,
            'details': details or {}
        }
        self.audit_trail.append(entry)
    
    def link_event(self, event_id: str):
        """Link to a UniversalEventRecord."""
        if event_id not in self.related_events:
            self.related_events.append(event_id)
    
    def link_hypothesis(self, hypothesis_id: str):
        """Link to a ParallelHypotheses."""
        if hypothesis_id not in self.related_hypotheses:
            self.related_hypotheses.append(hypothesis_id)
    
    def is_complete(self) -> bool:
        """Check if intent has been completed (post-action recorded)."""
        return self.post_action is not None
    
    def success_rate(self) -> float:
        """
        Calculate success rate based on success criteria.
        
        Returns:
            Float 0.0-1.0 indicating how many criteria were met
        """
        if not self.is_complete() or not self.pre_action.success_criteria:
            return 0.0
        
        # This is a simple implementation - in practice, you'd evaluate each criterion
        # For now, we use payoff as a proxy for success
        return self.post_action.payoff if self.post_action else 0.0
    
    def confidence_vs_outcome_gap(self) -> float:
        """
        Calculate gap between pre-action confidence and actual outcome.
        
        Returns:
            Float: gap = |confidence - payoff|. Large gaps indicate calibration issues.
        """
        if not self.is_complete():
            return 0.0
        
        return abs(self.pre_action.confidence - self.post_action.payoff)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'token_id': self.token_id,
            'created_at': self.created_at.isoformat(),
            'pre_action': self.pre_action.to_dict(),
            'post_action': self.post_action.to_dict() if self.post_action else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'measurements': self.measurements,
            'audit_trail': self.audit_trail,
            'attributed_to': self.attributed_to,
            'bounded_identity': self.bounded_identity,
            'related_events': self.related_events,
            'related_hypotheses': self.related_hypotheses,
            'version': self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntentToken':
        """Create IntentToken from dictionary."""
        # Parse timestamps
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('completed_at'), str):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        
        # Parse pre_action
        if isinstance(data.get('pre_action'), dict):
            data['pre_action'] = PreAction.from_dict(data['pre_action'])
        
        # Parse post_action
        if data.get('post_action') and isinstance(data['post_action'], dict):
            data['post_action'] = PostAction.from_dict(data['post_action'])
        
        return cls(**data)
    
    def save_to_log(self, log_path: str):
        """Append this intent to a JSONL log file."""
        import os
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'a') as f:
            json.dump(self.to_dict(), f)
            f.write('\n')
    
    @staticmethod
    def load_from_log(log_path: str) -> List['IntentToken']:
        """Load all intents from a JSONL log file."""
        intents = []
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        intents.append(IntentToken.from_dict(data))
        except FileNotFoundError:
            pass
        
        return intents
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        status = "complete" if self.is_complete() else "pending"
        return (
            f"IntentToken("
            f"id={self.token_id[:8]}..., "
            f"goal='{self.pre_action.goal[:30]}...', "
            f"status={status})"
        )


if __name__ == "__main__":
    # Demo: Create and complete an intent
    print("🎯 IntentToken Demo")
    print("=" * 50)
    
    # Create intent (pre-action)
    intent = IntentToken(
        pre_action=PreAction(
            goal="Retrieve user profile data",
            constraints=[
                "Must use cached data if < 5 min old",
                "Response time < 100ms",
                "Must include privacy settings"
            ],
            success_criteria=[
                "Got complete profile",
                "Response time met",
                "Privacy settings included"
            ],
            confidence=0.85
        ),
        attributed_to="agent_retriever_001"
    )
    
    print(f"\n✅ Created: {intent}")
    print(f"\n📋 Pre-Action:")
    print(f"   Goal: {intent.pre_action.goal}")
    print(f"   Confidence: {intent.pre_action.confidence}")
    print(f"   Constraints: {len(intent.pre_action.constraints)}")
    print(f"   Success Criteria: {len(intent.pre_action.success_criteria)}")
    
    # Add initial audit entry
    intent.add_audit_entry("created", "agent_retriever_001", {"phase": "pre-action"})
    
    # Simulate action execution
    print(f"\n⚙️  Executing action...")
    import time
    time.sleep(0.05)  # Simulate work
    
    # Add measurements
    intent.add_measurement("latency_ms", 48, "milliseconds")
    intent.add_measurement("cache_hit", True, "boolean")
    intent.add_measurement("data_size_kb", 12.5, "kilobytes")
    
    # Complete intent (post-action)
    intent.complete(
        trigger="user_profile_request",
        final_state={
            "profile_retrieved": True,
            "cache_used": True,
            "latency_ms": 48,
            "privacy_included": True
        },
        payoff=0.92  # High success (met criteria, fast response)
    )
    
    print(f"\n✅ Completed: {intent}")
    print(f"\n📊 Post-Action:")
    print(f"   Trigger: {intent.post_action.trigger}")
    print(f"   Payoff: {intent.post_action.payoff}")
    print(f"   Final State Keys: {list(intent.post_action.final_state.keys())}")
    
    print(f"\n📏 Measurements: {len(intent.measurements)}")
    for m in intent.measurements:
        print(f"   - {m['metric']}: {m['value']} {m['unit'] or ''}")
    
    print(f"\n📝 Audit Trail: {len(intent.audit_trail)} entries")
    for entry in intent.audit_trail:
        print(f"   - {entry['action']} by {entry['actor']}")
    
    # Analysis
    gap = intent.confidence_vs_outcome_gap()
    print(f"\n📈 Analysis:")
    print(f"   Success Rate: {intent.success_rate():.2%}")
    print(f"   Confidence Gap: {gap:.3f}")
    print(f"   (Small gap = well-calibrated, large gap = overconfident/underconfident)")
    
    # Save to log
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "intents.jsonl")
        intent.save_to_log(log_path)
        print(f"\n💾 Saved to: {log_path}")
        
        # Load back
        loaded = IntentToken.load_from_log(log_path)
        print(f"✅ Loaded {len(loaded)} intent(s) from log")
    
    print("\n" + "=" * 50)
    print("✅ Demo complete!")
