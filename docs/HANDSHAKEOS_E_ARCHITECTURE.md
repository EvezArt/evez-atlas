# HandshakeOS-E Nervous System

## Vision

HandshakeOS-E is a nervous system architecture designed to address the fundamental problem: **"fragmentation made it impossible to know what's true."**

The system provides a universal framework for tracking events, intentions, hypotheses, and tests without forcing any single domain interpretation. Truth emerges from user-driven tests and observable evidence, not from pre-imposed categorizations.

## Core Architecture

### 1. Universal Event Record

**Purpose**: Represent any system event without domain constraints.

**Key Features**:
- Domain-agnostic event tracking
- Optional domain mixture vectors (can be empty/unknown)
- Multiple source types (user input, device logs, user tests)
- Full versioning and auditability
- Immutable append-only logging

**Example**:
```python
from src.handshakeos import UniversalEventRecord, EventSource, DomainMixtureVector

# Create event with unknown domain mixture
event = UniversalEventRecord(
    event_type="user_interaction",
    payload={"action": "click", "target": "button_A"},
    source=EventSource.USER_INPUT,
    source_details="Web UI interaction"
)

# Later, refine with domain mixture as we learn more
mixture = DomainMixtureVector(
    social_dynamics=0.3,
    model_interaction=0.7,
    confidence=0.6
)
refined_event = event.refine_domain_mixture(mixture)
```

### 2. Intent Token

**Purpose**: Track the complete lifecycle of an intent from goal to outcome.

**Structure**:
- **Pre-Action**: Goal, constraints, success signals, confidence
- **Post-Event**: Trigger, resulting state, default policy, actual payoff

**Example**:
```python
from src.handshakeos import IntentToken

# Create and set pre-action intent
intent = IntentToken()
intent.set_pre_action(
    goal="Improve response time",
    constraints=["No breaking changes", "Keep API compatible"],
    success_signals=["Response < 100ms", "No errors in logs"],
    confidence=0.7
)

# Execute action
intent.start_execution()

# Capture post-event readout
intent.set_post_event(
    trigger="Performance optimization request",
    resulting_state={"response_time_ms": 85, "errors": 0},
    payoff=0.8,  # Positive outcome
    default_policy_outcome="Would have kept 200ms response time"
)

# Check success
success = intent.calculate_success()  # Returns True
```

### 3. Hypothesis System

**Purpose**: Track parallel hypotheses from multiple perspectives (me/we/they/system).

**Key Features**:
- No single "correct" model
- Each perspective has probability, falsifiers, domain mixture
- Consensus and divergence metrics
- Explicit falsification criteria

**Example**:
```python
from src.handshakeos import Hypothesis, ModelPerspective

# Create hypothesis
hypothesis = Hypothesis(
    name="Response time improvement hypothesis",
    description="Caching will reduce response times"
)

# Add model from "me" perspective
me_model = hypothesis.add_model(
    perspective=ModelPerspective.ME,
    description="I think caching will help",
    probability=0.8
)
me_model.add_falsifier(
    condition="Response time increases after caching",
    test_procedure="Measure before/after latency"
)

# Add model from "system" perspective
sys_model = hypothesis.add_model(
    perspective=ModelPerspective.SYSTEM,
    description="System metrics suggest memory constraints",
    probability=0.6
)

# Check consensus
consensus = hypothesis.get_consensus_probability()  # 0.7
divergence = hypothesis.get_perspective_divergence()  # 0.1
```

### 4. Test Objects

**Purpose**: First-class test objects that drive knowability.

**Key Features**:
- Linked to hypotheses
- Execution history tracking
- User-driven or automated
- Evidence gathering

**Example**:
```python
from src.handshakeos import TestObject, TestType

# Create test linked to hypothesis
test = TestObject(
    name="Cache performance test",
    description="Measure response time with caching enabled",
    test_type=TestType.USER_DRIVEN,
    procedure="Enable cache, send 100 requests, measure latency"
)
test.link_hypothesis(hypothesis.hypothesis_id)

# Execute test
def run_performance_test():
    # ... actual test logic ...
    return {
        'passed': True,
        'measurements': {'avg_latency_ms': 85, 'requests': 100},
        'observations': ['No errors', 'Memory usage stable']
    }

result = test.execute(run_performance_test)
print(f"Test {result.status}: {result.measurements}")
```

## Design Principles

### 1. No Mandatory Single-Domain Labels

Events and hypotheses exist without forced categorization. Domain mixtures are:
- **Optional**: Can be completely empty/unknown
- **Refined later**: As understanding emerges
- **Multi-domain**: Events can span multiple domains simultaneously

### 2. Knowability from Observable Sources

All knowledge comes from:
- **User input**: Direct user actions and statements
- **Device logs**: Observable system behavior
- **User-driven tests**: Explicit experimentation

No assumed knowledge or invisible inference.

### 3. Parallel Hypothesis Tracking

The system maintains multiple perspectives simultaneously:
- **me**: First-person perspective
- **we**: Collective/group perspective  
- **they**: Third-party perspective
- **system**: System-level perspective

Truth emerges from convergence/divergence patterns, not single authority.

### 4. Auditable, Attributable, Reversible

Every operation follows AAR principles:
- **Auditable**: Full logging with timestamps and IDs
- **Attributable**: Clear source tracking for all data
- **Reversible**: Immutable records enable reconstruction

### 5. Tests as First-Class Objects

Tests aren't just code - they're tracked objects with:
- Explicit hypothesis links
- Execution history
- Success metrics
- Evidence trails

## System Integration

### Event Log

```python
from src.handshakeos.event_record import EventLog

# Initialize append-only event log
log = EventLog()  # Defaults to data/handshakeos_events.jsonl

# Append events
log.append(event)

# Query events
recent_events = log.query(
    event_type="user_interaction",
    start_time=time.time() - 3600  # Last hour
)
```

### Registries

```python
from src.handshakeos.intent_token import IntentRegistry
from src.handshakeos.hypothesis import HypothesisRegistry
from src.handshakeos.test_object import TestRegistry

# Initialize registries
intent_registry = IntentRegistry()
hypothesis_registry = HypothesisRegistry()
test_registry = TestRegistry()

# Register objects
intent_registry.register(intent)
hypothesis_registry.register(hypothesis)
test_registry.register(test)

# Query and analyze
metrics = intent_registry.get_metrics()
high_confidence = hypothesis_registry.get_high_confidence(threshold=0.8)
pending_tests = test_registry.get_pending_tests()
```

## Workflow Example

Complete workflow demonstrating system integration:

```python
from src.handshakeos import (
    UniversalEventRecord, EventSource,
    IntentToken, Hypothesis, ModelPerspective,
    TestObject, TestType
)
from src.handshakeos.event_record import EventLog

# 1. Record initial event
event = UniversalEventRecord(
    event_type="performance_concern",
    payload={"metric": "response_time", "value_ms": 250},
    source=EventSource.DEVICE_LOG
)

log = EventLog()
log.append(event)

# 2. Form intent to address concern
intent = IntentToken()
intent.set_pre_action(
    goal="Reduce response time to <100ms",
    constraints=["No breaking changes"],
    success_signals=["Metrics show <100ms"],
    confidence=0.7
)

# 3. Create hypothesis about solution
hypothesis = Hypothesis(
    name="Caching hypothesis",
    description="Adding cache layer will reduce response time"
)

# Add multiple perspectives
me_model = hypothesis.add_model(
    perspective=ModelPerspective.ME,
    description="Based on similar past optimizations",
    probability=0.8
)
me_model.add_falsifier(
    condition="Response time doesn't improve after caching"
)

sys_model = hypothesis.add_model(
    perspective=ModelPerspective.SYSTEM,
    description="Memory constraints may limit effectiveness",
    probability=0.6
)

# 4. Create test to verify hypothesis
test = TestObject(
    name="Cache effectiveness test",
    description="Measure response time before and after caching",
    test_type=TestType.USER_DRIVEN
)
test.link_hypothesis(hypothesis.hypothesis_id)

# 5. Execute test
def cache_test():
    # Simulate test execution
    return {
        'passed': True,
        'measurements': {'response_time_ms': 85},
        'observations': ['Significant improvement', 'Memory usage acceptable']
    }

result = test.execute(cache_test)

# 6. Record outcome and complete intent
intent.start_execution()
intent.set_post_event(
    trigger="Performance optimization",
    resulting_state={"response_time_ms": 85},
    payoff=0.9,
    default_policy_outcome="250ms without intervention"
)

# 7. Update hypothesis based on evidence
if result.passed:
    me_model.update_probability(0.95, basis="Test confirmed hypothesis")
    me_model.add_evidence(event.event_id, supports=True)

# 8. Record completion event
completion_event = UniversalEventRecord(
    event_type="optimization_complete",
    payload={"improvement": "66% reduction", "final_ms": 85},
    source=EventSource.USER_TEST,
    related_events=[event.event_id],
    related_intents=[intent.intent_id],
    related_hypotheses=[hypothesis.hypothesis_id]
)
log.append(completion_event)
```

## File Structure

```
src/handshakeos/
├── __init__.py              # Package exports
├── event_record.py          # UniversalEventRecord, EventLog
├── intent_token.py          # IntentToken, PreActionIntent, PostEventCausal
├── hypothesis.py            # Hypothesis, ParallelModel, Falsifier
└── test_object.py           # TestObject, TestResult
```

## Data Storage

All data stored in append-only JSONL format:

```
data/
└── handshakeos_events.jsonl  # Event log (append-only)
```

Additional registries can be persisted as needed.

## Future Extensions

The architecture supports future extensions:

1. **Domain mixture refinement**: Machine learning to discover emergent patterns
2. **Causal inference**: Link events through causal chains
3. **Multi-agent coordination**: Share hypotheses across agents
4. **Temporal reasoning**: Track hypothesis evolution over time
5. **Conflict resolution**: Handle contradictory evidence systematically

## Philosophy

HandshakeOS-E embraces uncertainty and multiplicity:

- **Not knowing is OK**: Domain mixtures can be empty
- **Multiple truths coexist**: Parallel models without forced resolution
- **Tests drive knowledge**: Explicit experimentation over assumption
- **Emergent understanding**: Patterns emerge from data, not imposed top-down

The system fights fragmentation by providing universal structures that can represent any perspective without enforcing a single interpretation.

## Getting Started

See the demo script for a complete working example:

```bash
python demos/handshakeos_demo.py
```

Or run tests:

```bash
pytest tests/test_handshakeos.py -v
```
