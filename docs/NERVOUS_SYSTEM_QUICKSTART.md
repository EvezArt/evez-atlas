# HandshakeOS-E Nervous System Quick Start

## Installation

No dependencies required - pure Python implementation.

```bash
# Navigate to repository
cd /path/to/Evez666

# Run demonstration
python scripts/demo_nervous_system.py

# Run tests
pytest tests/test_nervous_system.py -v
```

## 5-Minute Quick Start

### 1. Initialize the System

```python
from src.mastra.nervous_system import NervousSystem, Actor

# Create nervous system instance
ns = NervousSystem()

# Register an actor (required for attribution)
actor = Actor(name="MyAgent", type="agent")
ns.register_actor(actor)
```

### 2. Record Events with Intent and Readout

```python
from src.mastra.nervous_system import IntentToken, EventReadout

# Declare intent before action
intent = IntentToken(
    goal="Process data",
    constraints=["Under 5 seconds"],
    confidence=0.8
)

# Record event
event = ns.record_event(actor_id=actor.id, intent=intent)

# After action, record readout
readout = EventReadout(
    trigger="user_request",
    result_state={"status": "success"},
    success=True,
    payoff=1.0
)
ns.update_event(event.id, readout=readout)
```

### 3. Track Hypotheses

```python
from src.mastra.nervous_system import ModelType

# Create hypothesis
hypothesis = ns.create_hypothesis(
    model_type=ModelType.ME,  # or WE, THEY, SYSTEM
    description="I process requests in <5s 90% of the time",
    probability=0.85,
    falsifiers=["Avg time > 5 seconds"]
)
```

### 4. Link Tests to Hypotheses

```python
# Create test
test = ns.create_test(
    name="test_processing_time",
    hypothesis_id=hypothesis.id,
    test_code="def test(): ..."
)

# Record test result
ns.record_test_result(
    test_id=test.id,
    passed=True,
    result={"avg_time": 4.2}
)
```

### 5. Query and Audit

```python
# Get all events by actor
events = ns.query_events(actor_id=actor.id)

# Get attribution
attribution = ns.get_attribution(event.id)

# Get full audit trail (all versions)
trail = ns.get_audit_trail(event.id)

# Get system stats
stats = ns.get_stats()
```

## Key Concepts

### Universal Events
- Domain-agnostic: no single-domain bias
- Mixture vectors: emergent domain signatures
- Intent + Readout: before and after tracking

### Parallel Models
- **ME**: Self-understanding
- **WE**: Team/collective understanding
- **THEY**: External agents/users
- **SYSTEM**: Environment/infrastructure

Track all four in parallel for complete picture.

### Attribution
- Every event linked to an actor
- No invisible agents
- Complete audit trail
- Version tracking for rollback

## Common Patterns

### Wrap Existing Functions

```python
def my_function(data):
    # Declare intent
    intent = IntentToken(goal="Process data", confidence=0.9)
    event = ns.record_event(actor_id=actor.id, intent=intent)
    
    try:
        result = process(data)
        readout = EventReadout(
            trigger="function_call",
            success=True,
            payoff=1.0
        )
    except Exception as e:
        readout = EventReadout(
            trigger="function_call",
            success=False,
            payoff=0.0
        )
        raise
    finally:
        ns.update_event(event.id, readout=readout)
    
    return result
```

### Test Integration

```python
def test_my_feature():
    # Create hypothesis
    hyp = ns.create_hypothesis(
        model_type=ModelType.SYSTEM,
        description="Feature works correctly"
    )
    
    # Create test
    test = ns.create_test(
        name="test_my_feature",
        hypothesis_id=hyp.id
    )
    
    # Run test
    try:
        assert my_feature() == expected
        passed = True
    except:
        passed = False
    
    # Record result
    ns.record_test_result(test.id, passed=passed, result={})
```

### Mixture Vectors (Emergent Domains)

```python
from src.mastra.nervous_system import MixtureVector

# Create domain signature
mixture = MixtureVector(
    components={
        "computation": 0.3,
        "user_interaction": 0.5,
        "data_access": 0.2
    }
)
mixture.normalize()  # Ensure weights sum to 1.0

# Use in event
event = ns.record_event(
    actor_id=actor.id,
    mixture=mixture
)
```

## File Structure

```
data/nervous_system/
├── events.jsonl       # All events (append-only)
├── hypotheses.jsonl   # All hypotheses
├── tests.jsonl        # All tests
└── actors.jsonl       # Actor registry
```

Each file is JSONL (JSON Lines): one JSON object per line.

## Best Practices

1. **Always register actors** before recording events
2. **Declare intent** before taking action
3. **Record readout** after action completes
4. **Track all four model types** for complete understanding
5. **Link tests to hypotheses** for validation
6. **Query regularly** to understand system behavior
7. **Use audit trail** for debugging and rollback

## Example Use Cases

### API Endpoint Monitoring

```python
# Before handling request
intent = IntentToken(
    goal="Handle API request",
    constraints=["<200ms latency"],
    confidence=0.9
)
event = ns.record_event(actor_id=api_actor.id, intent=intent)

# After handling request
readout = EventReadout(
    trigger="api_request",
    result_state={"status_code": 200, "latency_ms": 150},
    success=True,
    payoff=1.0
)
ns.update_event(event.id, readout=readout)
```

### Hypothesis Testing

```python
# Hypothesis: API responds in <200ms 95% of the time
hyp = ns.create_hypothesis(
    model_type=ModelType.SYSTEM,
    description="API <200ms latency 95% of time",
    probability=0.80,
    falsifiers=["95th percentile > 200ms"]
)

# Test it
test = ns.create_test(
    name="test_api_latency",
    hypothesis_id=hyp.id
)

# Run load test and record results
ns.record_test_result(
    test_id=test.id,
    passed=True,
    result={"p95_latency_ms": 180}
)

# Update hypothesis
ns.update_hypothesis(hyp.id, probability=0.95)
```

## Troubleshooting

### "Actor not registered" error
Register actor before recording events:
```python
actor = Actor(name="MyActor", type="agent")
ns.register_actor(actor)
```

### Can't find events
Check data directory location:
```python
print(ns.data_dir)  # Default: data/nervous_system
```

### Need to reset data
```bash
rm -rf data/nervous_system/
```

## Next Steps

1. Read [full documentation](../docs/NERVOUS_SYSTEM.md)
2. Run [demo script](../scripts/demo_nervous_system.py)
3. Explore [test examples](../tests/test_nervous_system.py)
4. Integrate with your project

## Support

See the [main documentation](../docs/NERVOUS_SYSTEM.md) for:
- Architecture details
- API reference
- Design principles
- Integration examples
- Performance considerations
