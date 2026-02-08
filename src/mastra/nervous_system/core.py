"""
Core data structures for HandshakeOS-E Nervous System.

This module implements the foundational components for a domain-agnostic
event recording and hypothesis tracking system.

Design Principles:
1. Universal event records: no single-domain bias
2. Mixture vectors: domains are emergent from data
3. Attribution: every intervention linked to an actor
4. Auditability: full trace with versioning
5. Reversibility: rollback support built-in

For the future maintainer:
- All IDs are UUIDs for global uniqueness
- Timestamps are ISO 8601 UTC strings
- Mixture vectors can start empty/unknown and refine over time
- The system is designed to never lose information
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class ModelType(Enum):
    """Hypothesis model types for parallel tracking."""
    ME = "me"          # Self model
    WE = "we"          # Collective/team model
    THEY = "they"      # Other agents/external model
    SYSTEM = "system"  # System/environment model


@dataclass
class MixtureVector:
    """
    Domain-agnostic mixture vector.
    
    Represents emergent domain signature without hard-coding domains.
    Can start empty and refine over time as patterns emerge.
    
    Attributes:
        components: Dict mapping component names to weights
        normalized: Whether weights sum to 1.0
        metadata: Additional context (can include confidence, source, etc.)
    """
    components: Dict[str, float] = field(default_factory=dict)
    normalized: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def normalize(self) -> 'MixtureVector':
        """Normalize weights to sum to 1.0."""
        total = sum(self.components.values())
        if total > 0:
            self.components = {k: v/total for k, v in self.components.items()}
            self.normalized = True
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class Actor:
    """
    Identity for attribution.
    
    Every intervention must be linked to an actor. No invisible agents.
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        type: Type of actor (human, agent, system, etc.)
        permissions: Set of allowed operations
        metadata: Additional context
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = "unknown"
    permissions: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['permissions'] = list(self.permissions)  # Set -> List for JSON
        return data


@dataclass
class IntentToken:
    """
    Pre-action intent declaration.
    
    Captures what the actor intends to do before doing it.
    Makes goals, constraints, and success criteria explicit.
    
    Attributes:
        goal: What the actor is trying to achieve
        constraints: Limitations or requirements
        success_metric: How to measure success
        confidence: Actor's confidence in achieving goal (0-1)
        metadata: Additional context
    """
    goal: str
    constraints: List[str] = field(default_factory=list)
    success_metric: str = ""
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class EventReadout:
    """
    Post-event analysis.
    
    Captures what actually happened and the outcomes.
    
    Attributes:
        trigger: What caused this event
        result_state: Resulting state after event
        policy_used: Which policy/rule was applied
        payoff: Measured outcome/value
        success: Whether intent was achieved
        metadata: Additional context
    """
    trigger: str
    result_state: Dict[str, Any] = field(default_factory=dict)
    policy_used: str = "default"
    payoff: float = 0.0
    success: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class UniversalEvent:
    """
    Universal event record.
    
    Capable of representing:
    - Internal state shifts
    - Device/OS routing
    - Network/session negotiations
    - Social/incentive dynamics
    - Model-to-user interactions
    
    No bias toward a single domain. Mixture vectors are emergent.
    
    Attributes:
        id: Unique event identifier
        actor_id: Who initiated this event
        intent: Pre-action intent token
        readout: Post-event readout
        mixture: Domain signature (emergent)
        related_events: IDs of related events
        version: Version number for rollback
        metadata: Additional context
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str = ""
    intent: Optional[IntentToken] = None
    readout: Optional[EventReadout] = None
    mixture: MixtureVector = field(default_factory=MixtureVector)
    related_events: List[str] = field(default_factory=list)
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            'id': self.id,
            'actor_id': self.actor_id,
            'intent': self.intent.to_dict() if self.intent else None,
            'readout': self.readout.to_dict() if self.readout else None,
            'mixture': self.mixture.to_dict(),
            'related_events': self.related_events,
            'version': self.version,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        return data


@dataclass
class Hypothesis:
    """
    Hypothesis for parallel model tracking.
    
    Tracks me/we/they/system models in parallel, each with:
    - Probability estimate
    - Falsifier conditions
    - Mixture vector for domain signature
    
    Attributes:
        id: Unique identifier
        model_type: Which model this hypothesis belongs to
        description: Human-readable hypothesis statement
        probability: Current probability estimate (0-1)
        falsifiers: Conditions that would falsify this hypothesis
        mixture: Domain signature
        linked_tests: Test IDs validating this hypothesis
        evidence: Supporting/contradicting evidence
        version: Version number
        metadata: Additional context
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_type: ModelType = ModelType.SYSTEM
    description: str = ""
    probability: float = 0.5
    falsifiers: List[str] = field(default_factory=list)
    mixture: MixtureVector = field(default_factory=MixtureVector)
    linked_tests: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)  # Event IDs
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['model_type'] = self.model_type.value
        data['mixture'] = self.mixture.to_dict()
        return data


@dataclass
class Test:
    """
    First-class test object.
    
    Tests are linked to hypotheses and provide validation.
    
    Attributes:
        id: Unique identifier
        name: Test name
        hypothesis_id: Hypothesis this test validates
        test_code: Test implementation (can be code, procedure, etc.)
        passed: Whether test passed
        result: Test result/output
        version: Version number
        metadata: Additional context
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    hypothesis_id: str = ""
    test_code: str = ""
    passed: Optional[bool] = None
    result: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    executed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class NervousSystem:
    """
    Main nervous system coordinator.
    
    Manages the event log, hypotheses, tests, and actors.
    Ensures all interventions are auditable, attributable, and reversible.
    
    This is the public API for the HandshakeOS-E nervous system.
    
    Design principles:
    - Append-only event log (never delete)
    - Full attribution (every action linked to actor)
    - Versioning support (enable rollback)
    - Query and audit capabilities
    
    For the future maintainer:
    - Events are stored in JSONL format for easy streaming
    - All data structures serialize to JSON
    - The system is designed to scale to millions of events
    - Consider adding indexing for large-scale deployments
    """
    
    def __init__(self, data_dir: Path = None):
        """
        Initialize nervous system.
        
        Args:
            data_dir: Directory for storing event logs and data.
                     Defaults to ./data/nervous_system
        """
        if data_dir is None:
            data_dir = Path("data/nervous_system")
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.events_file = self.data_dir / "events.jsonl"
        self.hypotheses_file = self.data_dir / "hypotheses.jsonl"
        self.tests_file = self.data_dir / "tests.jsonl"
        self.actors_file = self.data_dir / "actors.jsonl"
        
        # In-memory caches (for performance)
        self._events: Dict[str, UniversalEvent] = {}
        self._hypotheses: Dict[str, Hypothesis] = {}
        self._tests: Dict[str, Test] = {}
        self._actors: Dict[str, Actor] = {}
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load data from disk into memory."""
        # Load events
        if self.events_file.exists():
            with open(self.events_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    event = self._dict_to_event(data)
                    self._events[event.id] = event
        
        # Load hypotheses
        if self.hypotheses_file.exists():
            with open(self.hypotheses_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    hyp = self._dict_to_hypothesis(data)
                    self._hypotheses[hyp.id] = hyp
        
        # Load tests
        if self.tests_file.exists():
            with open(self.tests_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    test = self._dict_to_test(data)
                    self._tests[test.id] = test
        
        # Load actors
        if self.actors_file.exists():
            with open(self.actors_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    actor = self._dict_to_actor(data)
                    self._actors[actor.id] = actor
    
    def _dict_to_event(self, data: Dict) -> UniversalEvent:
        """Convert dictionary to UniversalEvent."""
        intent = None
        if data.get('intent'):
            intent = IntentToken(**data['intent'])
        
        readout = None
        if data.get('readout'):
            readout = EventReadout(**data['readout'])
        
        mixture = MixtureVector(**data.get('mixture', {}))
        
        return UniversalEvent(
            id=data['id'],
            actor_id=data['actor_id'],
            intent=intent,
            readout=readout,
            mixture=mixture,
            related_events=data.get('related_events', []),
            version=data.get('version', 1),
            metadata=data.get('metadata', {}),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
        )
    
    def _dict_to_hypothesis(self, data: Dict) -> Hypothesis:
        """Convert dictionary to Hypothesis."""
        model_type = ModelType(data['model_type'])
        mixture = MixtureVector(**data.get('mixture', {}))
        
        return Hypothesis(
            id=data['id'],
            model_type=model_type,
            description=data['description'],
            probability=data['probability'],
            falsifiers=data.get('falsifiers', []),
            mixture=mixture,
            linked_tests=data.get('linked_tests', []),
            evidence=data.get('evidence', []),
            version=data.get('version', 1),
            metadata=data.get('metadata', {}),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
        )
    
    def _dict_to_test(self, data: Dict) -> Test:
        """Convert dictionary to Test."""
        return Test(**data)
    
    def _dict_to_actor(self, data: Dict) -> Actor:
        """Convert dictionary to Actor."""
        data['permissions'] = set(data.get('permissions', []))
        return Actor(**data)
    
    def _append_to_file(self, file_path: Path, data: Dict):
        """Append data to JSONL file."""
        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    # ====== Actor Management ======
    
    def register_actor(self, actor: Actor) -> Actor:
        """
        Register a new actor.
        
        Args:
            actor: Actor to register
            
        Returns:
            Registered actor with ID
        """
        self._actors[actor.id] = actor
        self._append_to_file(self.actors_file, actor.to_dict())
        return actor
    
    def get_actor(self, actor_id: str) -> Optional[Actor]:
        """Get actor by ID."""
        return self._actors.get(actor_id)
    
    # ====== Event Management ======
    
    def record_event(
        self,
        actor_id: str,
        intent: Optional[IntentToken] = None,
        readout: Optional[EventReadout] = None,
        mixture: Optional[MixtureVector] = None,
        related_events: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UniversalEvent:
        """
        Record a universal event.
        
        Args:
            actor_id: ID of actor initiating event
            intent: Pre-action intent (optional, can be added later)
            readout: Post-event readout (optional, can be added later)
            mixture: Domain signature (optional, can be refined later)
            related_events: IDs of related events
            metadata: Additional context
            
        Returns:
            Created event
            
        Raises:
            ValueError: If actor_id is not registered
        """
        if actor_id not in self._actors:
            raise ValueError(f"Actor {actor_id} not registered")
        
        event = UniversalEvent(
            actor_id=actor_id,
            intent=intent,
            readout=readout,
            mixture=mixture or MixtureVector(),
            related_events=related_events or [],
            metadata=metadata or {},
        )
        
        self._events[event.id] = event
        self._append_to_file(self.events_file, event.to_dict())
        
        return event
    
    def update_event(
        self,
        event_id: str,
        intent: Optional[IntentToken] = None,
        readout: Optional[EventReadout] = None,
        mixture: Optional[MixtureVector] = None,
    ) -> UniversalEvent:
        """
        Update an existing event.
        
        Creates a new version of the event (for auditability).
        
        Args:
            event_id: ID of event to update
            intent: Updated intent
            readout: Updated readout
            mixture: Updated mixture
            
        Returns:
            Updated event
            
        Raises:
            ValueError: If event not found
        """
        if event_id not in self._events:
            raise ValueError(f"Event {event_id} not found")
        
        event = self._events[event_id]
        event.version += 1
        event.updated_at = datetime.utcnow().isoformat()
        
        if intent is not None:
            event.intent = intent
        if readout is not None:
            event.readout = readout
        if mixture is not None:
            event.mixture = mixture
        
        self._append_to_file(self.events_file, event.to_dict())
        
        return event
    
    def get_event(self, event_id: str) -> Optional[UniversalEvent]:
        """Get event by ID."""
        return self._events.get(event_id)
    
    def query_events(
        self,
        actor_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[UniversalEvent]:
        """
        Query events with filters.
        
        Args:
            actor_id: Filter by actor
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            
        Returns:
            List of matching events
        """
        events = list(self._events.values())
        
        if actor_id:
            events = [e for e in events if e.actor_id == actor_id]
        
        if start_time:
            events = [e for e in events if e.created_at >= start_time]
        
        if end_time:
            events = [e for e in events if e.created_at <= end_time]
        
        return events
    
    # ====== Hypothesis Management ======
    
    def create_hypothesis(
        self,
        model_type: ModelType,
        description: str,
        probability: float = 0.5,
        falsifiers: Optional[List[str]] = None,
        mixture: Optional[MixtureVector] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Hypothesis:
        """
        Create a new hypothesis.
        
        Args:
            model_type: Type of model (me/we/they/system)
            description: Hypothesis statement
            probability: Initial probability estimate
            falsifiers: Conditions that would falsify hypothesis
            mixture: Domain signature
            metadata: Additional context
            
        Returns:
            Created hypothesis
        """
        hyp = Hypothesis(
            model_type=model_type,
            description=description,
            probability=probability,
            falsifiers=falsifiers or [],
            mixture=mixture or MixtureVector(),
            metadata=metadata or {},
        )
        
        self._hypotheses[hyp.id] = hyp
        self._append_to_file(self.hypotheses_file, hyp.to_dict())
        
        return hyp
    
    def update_hypothesis(
        self,
        hypothesis_id: str,
        probability: Optional[float] = None,
        add_evidence: Optional[str] = None,
        add_test: Optional[str] = None,
    ) -> Hypothesis:
        """
        Update hypothesis with new evidence or test.
        
        Creates a new version (for auditability).
        
        Args:
            hypothesis_id: ID of hypothesis to update
            probability: Updated probability
            add_evidence: Event ID to add as evidence
            add_test: Test ID to link
            
        Returns:
            Updated hypothesis
            
        Raises:
            ValueError: If hypothesis not found
        """
        if hypothesis_id not in self._hypotheses:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")
        
        hyp = self._hypotheses[hypothesis_id]
        hyp.version += 1
        hyp.updated_at = datetime.utcnow().isoformat()
        
        if probability is not None:
            hyp.probability = probability
        
        if add_evidence and add_evidence not in hyp.evidence:
            hyp.evidence.append(add_evidence)
        
        if add_test and add_test not in hyp.linked_tests:
            hyp.linked_tests.append(add_test)
        
        self._append_to_file(self.hypotheses_file, hyp.to_dict())
        
        return hyp
    
    def get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        """Get hypothesis by ID."""
        return self._hypotheses.get(hypothesis_id)
    
    def get_hypotheses_by_model(self, model_type: ModelType) -> List[Hypothesis]:
        """Get all hypotheses for a specific model type."""
        return [h for h in self._hypotheses.values() if h.model_type == model_type]
    
    # ====== Test Management ======
    
    def create_test(
        self,
        name: str,
        hypothesis_id: str,
        test_code: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Test:
        """
        Create a test linked to a hypothesis.
        
        Args:
            name: Test name
            hypothesis_id: Hypothesis this test validates
            test_code: Test implementation
            metadata: Additional context
            
        Returns:
            Created test
            
        Raises:
            ValueError: If hypothesis not found
        """
        if hypothesis_id not in self._hypotheses:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")
        
        test = Test(
            name=name,
            hypothesis_id=hypothesis_id,
            test_code=test_code,
            metadata=metadata or {},
        )
        
        self._tests[test.id] = test
        self._append_to_file(self.tests_file, test.to_dict())
        
        # Link test to hypothesis
        self.update_hypothesis(hypothesis_id, add_test=test.id)
        
        return test
    
    def record_test_result(
        self,
        test_id: str,
        passed: bool,
        result: Dict[str, Any],
    ) -> Test:
        """
        Record test execution result.
        
        Args:
            test_id: ID of test
            passed: Whether test passed
            result: Test result/output
            
        Returns:
            Updated test
            
        Raises:
            ValueError: If test not found
        """
        if test_id not in self._tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self._tests[test_id]
        test.version += 1
        test.passed = passed
        test.result = result
        test.executed_at = datetime.utcnow().isoformat()
        
        self._append_to_file(self.tests_file, test.to_dict())
        
        return test
    
    def get_test(self, test_id: str) -> Optional[Test]:
        """Get test by ID."""
        return self._tests.get(test_id)
    
    def get_tests_for_hypothesis(self, hypothesis_id: str) -> List[Test]:
        """Get all tests for a hypothesis."""
        return [t for t in self._tests.values() if t.hypothesis_id == hypothesis_id]
    
    # ====== Audit and Rollback ======
    
    def get_audit_trail(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get full audit trail for an entity (event, hypothesis, test).
        
        Shows all versions and changes over time.
        
        Args:
            entity_id: ID of entity to audit
            
        Returns:
            List of all versions of the entity
        """
        trail = []
        
        # Check events file
        if self.events_file.exists():
            with open(self.events_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    if data.get('id') == entity_id:
                        trail.append(data)
        
        # Check hypotheses file
        if self.hypotheses_file.exists():
            with open(self.hypotheses_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    if data.get('id') == entity_id:
                        trail.append(data)
        
        # Check tests file
        if self.tests_file.exists():
            with open(self.tests_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    if data.get('id') == entity_id:
                        trail.append(data)
        
        return trail
    
    def get_attribution(self, event_id: str) -> Dict[str, Any]:
        """
        Get full attribution for an event.
        
        Shows who did what and when.
        
        Args:
            event_id: ID of event
            
        Returns:
            Attribution information
        """
        event = self.get_event(event_id)
        if not event:
            return {}
        
        actor = self.get_actor(event.actor_id)
        
        return {
            'event_id': event_id,
            'actor': actor.to_dict() if actor else None,
            'created_at': event.created_at,
            'updated_at': event.updated_at,
            'version': event.version,
            'related_events': event.related_events,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            'total_events': len(self._events),
            'total_hypotheses': len(self._hypotheses),
            'total_tests': len(self._tests),
            'total_actors': len(self._actors),
            'hypotheses_by_model': {
                model.value: len(self.get_hypotheses_by_model(model))
                for model in ModelType
            },
        }
