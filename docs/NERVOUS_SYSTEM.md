# HandshakeOS-E Nervous System

## Overview

The HandshakeOS-E Nervous System is a domain-agnostic event recording and hypothesis tracking infrastructure designed to make every system interaction knowable, auditable, and reversible.

**Key Principles:**
- Make every handshake knowable
- Force projects to tell the truth
- Enable rapid fix/verify cycles
- Prevent organizational fragmentation
- Make rollback and attribution easy and safe

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Nervous System                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Universal    │  │  Hypothesis  │  │     Test     │    │
│  │   Events     │  │   Tracking   │  │   Objects    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         │                  └──────────────────┤            │
│         │                                     │            │
│  ┌──────▼──────────────────────────────────▼─────┐       │
│  │          Attribution & Audit Trail            │       │
│  └───────────────────────────────────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Structures

#### UniversalEvent
Domain-agnostic event record capable of representing:
- Internal state shifts
- Device/OS routing
- Network/session negotiations
- Social/incentive dynamics
- Model-to-user interactions

**Fields:**
- `id`: Unique identifier (UUID)
- `actor_id`: Who initiated this event
- `intent`: Pre-action IntentToken
- `readout`: Post-event EventReadout
- `mixture`: MixtureVector (emergent domain signature)
- `related_events`: Connected event IDs
- `version`: Version number for rollback
- `metadata`: Additional context

#### IntentToken (Pre-Action)
Declares intent before execution:
- `goal`: What the actor is trying to achieve
- `constraints`: Limitations or requirements
- `success_metric`: How to measure success
- `confidence`: Actor's confidence (0-1)

#### EventReadout (Post-Action)
Captures actual outcomes:
- `trigger`: What caused this event
- `result_state`: Resulting state
- `policy_used`: Which policy/rule was applied
- `payoff`: Measured outcome/value
- `success`: Whether intent was achieved

#### Hypothesis
Parallel model tracking (me/we/they/system):
- `model_type`: ME | WE | THEY | SYSTEM
- `description`: Hypothesis statement
- `probability`: Current estimate (0-1)
- `falsifiers`: Conditions that would falsify
- `mixture`: Domain signature
- `linked_tests`: Test IDs validating this hypothesis
- `evidence`: Event IDs as evidence

#### Test
First-class test objects:
- `name`: Test name
- `hypothesis_id`: Hypothesis this test validates
- `test_code`: Test implementation
- `passed`: Whether test passed
- `result`: Test result/output

#### Actor
Identity for attribution:
- `id`: Unique identifier
- `name`: Human-readable name
- `type`: Type of actor (human, agent, system)
- `permissions`: Allowed operations
- No invisible agents: every intervention is linked

#### MixtureVector
Domain-agnostic signature:
- `components`: Dict mapping component names to weights
- `normalized`: Whether weights sum to 1.0
- No single-domain bias: domains are emergent

## Usage Guide

### Basic Setup

```python
from src.mastra.nervous_system import (
    NervousSystem,
    Actor,
    IntentToken,
    EventReadout,
)

# Initialize nervous system
ns = NervousSystem()

# Register an actor (required for attribution)
actor = Actor(
    name="My Agent",
    type="agent",
    permissions={"record_events", "create_hypotheses"}
)
ns.register_actor(actor)
```

### Recording Events

```python
# Record event with intent
intent = IntentToken(
    goal="Process user request",
    constraints=["Must complete within 5 seconds"],
    success_metric="Request processed successfully",
    confidence=0.8
)

event = ns.record_event(
    actor_id=actor.id,
    intent=intent,
    metadata={"request_type": "data_query"}
)

# Later, update with readout
readout = EventReadout(
    trigger="user_request",
    result_state={"status": "success", "items": 42},
    policy_used="default_policy",
    payoff=1.0,
    success=True
)

ns.update_event(event.id, readout=readout)
```

### Tracking Hypotheses

```python
from src.mastra.nervous_system import ModelType

# ME model: Self-understanding
me_hypothesis = ns.create_hypothesis(
    model_type=ModelType.ME,
    description="I can process requests in <5s 90% of the time",
    probability=0.85,
    falsifiers=["Average processing time exceeds 5 seconds"]
)

# WE model: Team/collective
we_hypothesis = ns.create_hypothesis(
    model_type=ModelType.WE,
    description="Our system handles 1000 req/s with <100ms latency",
    probability=0.70,
    falsifiers=["Latency exceeds 100ms at 1000 req/s"]
)

# THEY model: External agents/users
they_hypothesis = ns.create_hypothesis(
    model_type=ModelType.THEY,
    description="Users prefer brief responses",
    probability=0.60
)

# SYSTEM model: Environment/infrastructure
system_hypothesis = ns.create_hypothesis(
    model_type=ModelType.SYSTEM,
    description="Connection pool of 20 is sufficient",
    probability=0.75
)
```

### Linking Tests to Hypotheses

```python
# Create test for hypothesis
test = ns.create_test(
    name="Test: Average processing time",
    hypothesis_id=me_hypothesis.id,
    test_code="""
def test_processing_time():
    times = measure_processing_times(n=100)
    avg_time = sum(times) / len(times)
    assert avg_time < 5.0
    """,
    metadata={"test_type": "performance"}
)

# Record test result
ns.record_test_result(
    test_id=test.id,
    passed=True,
    result={"average_time": 4.2, "samples": 100}
)

# Update hypothesis based on test
ns.update_hypothesis(
    me_hypothesis.id,
    probability=0.90  # Increased confidence after passing test
)
```

### Attribution and Audit

```python
# Get attribution for an event
attribution = ns.get_attribution(event.id)
print(f"Actor: {attribution['actor']['name']}")
print(f"Created: {attribution['created_at']}")

# Get complete audit trail (all versions)
trail = ns.get_audit_trail(event.id)
print(f"Total versions: {len(trail)}")

# Enables rollback: any version can be restored
for version in trail:
    print(f"Version {version['version']}: {version['updated_at']}")
```

### Query and Analysis

```python
# Query events by actor
events = ns.query_events(actor_id=actor.id)

# Query events by time range
events = ns.query_events(
    start_time="2024-01-01T00:00:00",
    end_time="2024-12-31T23:59:59"
)

# Get hypotheses by model type
me_hypotheses = ns.get_hypotheses_by_model(ModelType.ME)
we_hypotheses = ns.get_hypotheses_by_model(ModelType.WE)

# Get tests for hypothesis
tests = ns.get_tests_for_hypothesis(hypothesis_id)

# Get system statistics
stats = ns.get_stats()
print(f"Total events: {stats['total_events']}")
print(f"Total hypotheses: {stats['total_hypotheses']}")
```

## Design Principles

### 1. Universal Event Records
- No single-domain bias
- Mixture vectors only
- Domains are emergent from data
- Can start empty/unknown and refine over time

### 2. Explicit Intent and Readout
- Intent declared before action
- Readout captured after action
- Makes goals and outcomes explicit
- Forces truth-telling

### 3. Parallel Model Tracking
- ME: Self model
- WE: Collective/team model
- THEY: Other agents/external model
- SYSTEM: System/environment model

Track all four in parallel for complete understanding.

### 4. Test-Hypothesis Linkage
- Tests are first-class objects
- Bidirectionally linked to hypotheses
- Test results update hypothesis probabilities
- Enables rapid verify/fix cycles

### 5. Attribution and Auditability
- Every intervention linked to an actor
- No invisible agents
- Complete audit trail
- All versions preserved

### 6. Reversibility
- Versioning built-in
- Append-only event log
- Any version can be restored
- Safe rollback

## Data Storage

### File Structure
```
data/nervous_system/
├── events.jsonl       # Universal events
├── hypotheses.jsonl   # Hypothesis tracking
├── tests.jsonl        # Test objects
└── actors.jsonl       # Actor registry
```

### Format
All data stored in JSONL (JSON Lines) format:
- One JSON object per line
- Append-only (never delete)
- Easy streaming and processing
- Compatible with standard tools

### Persistence
- Automatic save on every operation
- Automatic load on initialization
- In-memory caching for performance
- Safe for concurrent reads

## Performance Considerations

### For Small to Medium Deployments (<1M events)
- In-memory caching provides fast access
- JSONL format is sufficient
- No additional infrastructure needed

### For Large Deployments (>1M events)
Consider:
- Adding indexing (e.g., SQLite, PostgreSQL)
- Implementing event log rotation
- Using time-series databases for queries
- Adding caching layer (Redis, Memcached)

## Integration Examples

### With Existing Systems

```python
# Wrap existing function
def my_existing_function(data):
    # Declare intent
    intent = IntentToken(
        goal="Process data",
        confidence=0.9
    )
    
    event = ns.record_event(
        actor_id=actor.id,
        intent=intent
    )
    
    try:
        result = existing_logic(data)
        
        # Record success
        readout = EventReadout(
            trigger="function_call",
            result_state={"result": result},
            success=True,
            payoff=1.0
        )
    except Exception as e:
        # Record failure
        readout = EventReadout(
            trigger="function_call",
            result_state={"error": str(e)},
            success=False,
            payoff=0.0
        )
        raise
    finally:
        ns.update_event(event.id, readout=readout)
    
    return result
```

### With Testing Frameworks

```python
# pytest integration
def test_my_hypothesis():
    # Create hypothesis
    hyp = ns.create_hypothesis(
        model_type=ModelType.SYSTEM,
        description="Database responds within 100ms"
    )
    
    # Create linked test
    test = ns.create_test(
        name="test_database_response_time",
        hypothesis_id=hyp.id
    )
    
    # Run test
    response_times = measure_db_response_times(n=100)
    passed = all(t < 0.1 for t in response_times)
    
    # Record result
    ns.record_test_result(
        test_id=test.id,
        passed=passed,
        result={
            "avg_time": sum(response_times) / len(response_times),
            "max_time": max(response_times),
            "samples": len(response_times)
        }
    )
    
    # Update hypothesis based on result
    if passed:
        ns.update_hypothesis(hyp.id, probability=0.95)
    else:
        ns.update_hypothesis(hyp.id, probability=0.30)
    
    assert passed
```

## API Reference

See inline documentation in `src/mastra/nervous_system/core.py` for complete API reference.

### Key Classes
- `NervousSystem`: Main coordinator
- `UniversalEvent`: Event record
- `IntentToken`: Pre-action intent
- `EventReadout`: Post-action readout
- `Hypothesis`: Model tracking
- `Test`: Test object
- `Actor`: Identity for attribution
- `MixtureVector`: Domain signature

### Key Methods

#### NervousSystem
- `register_actor(actor)`: Register new actor
- `record_event(...)`: Record universal event
- `update_event(...)`: Update event with readout
- `create_hypothesis(...)`: Create hypothesis
- `update_hypothesis(...)`: Update hypothesis
- `create_test(...)`: Create test linked to hypothesis
- `record_test_result(...)`: Record test execution
- `get_attribution(event_id)`: Get event attribution
- `get_audit_trail(entity_id)`: Get full audit trail
- `query_events(...)`: Query events with filters
- `get_stats()`: Get system statistics

## Future Maintainer Notes

### What This System Does
- Records all system interactions as universal events
- Tracks hypotheses about system behavior
- Links tests to hypotheses for validation
- Provides complete attribution and audit trail
- Enables safe rollback via versioning

### What This System Does NOT Do
- Does not execute tests automatically
- Does not analyze mixture vectors automatically
- Does not make decisions (it records decisions)
- Does not enforce policies (it records policies used)

### Extension Points
1. **Mixture Vector Analysis**: Add analysis of emergent domains
2. **Automatic Hypothesis Updates**: Update probabilities based on evidence
3. **Test Execution**: Integrate with test runners
4. **Visualization**: Add dashboards and graphs
5. **Indexing**: Add database backend for large-scale deployments
6. **Real-time Queries**: Add stream processing for live analysis

### Compatibility
- Python 3.7+
- No external dependencies (pure Python)
- JSON serialization for all data
- Compatible with existing pytest/unittest frameworks

### Migration Path
To add nervous system to existing project:
1. Initialize NervousSystem instance
2. Register actors for your agents/users
3. Wrap key functions with event recording
4. Create hypotheses about system behavior
5. Link existing tests to hypotheses
6. Query and analyze over time

## Demo

Run the demonstration:
```bash
python scripts/demo_nervous_system.py
```

This demonstrates:
- Event recording with intent/readout
- Mixture vectors
- Parallel hypothesis tracking
- Test linkage
- Attribution and auditability
- Rollback capability

## Testing

Run the test suite:
```bash
pytest tests/test_nervous_system.py -v
```

Coverage includes:
- Actor management
- Event recording and querying
- Hypothesis tracking
- Test linkage
- Attribution and audit
- Persistence
- System statistics

## License

See repository LICENSE file.

## Contributing

When contributing to this system:
1. Maintain domain-agnostic design
2. Preserve attribution and auditability
3. Never delete data (append-only)
4. Document for future maintainers
5. Include tests for new features
6. Follow existing patterns

## Questions?

For the future maintainer reading this:
- All IDs are UUIDs for global uniqueness
- Timestamps are ISO 8601 UTC strings
- Mixture vectors can start empty and refine over time
- The system is designed to never lose information
- Every intervention must be attributable
- Versioning enables safe rollback

Read the code comments for detailed explanations of each component.
