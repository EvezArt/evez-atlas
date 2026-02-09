# Entity Lifecycle Root Trace Integration

## Overview

This integration creates a **deep connection** between the entity lifecycle management system and the recursive-observer root trace functionality. This allows complete observability of entity "life" at the execution level.

## What It Does

- Records all entity lifecycle events (creation, awakening, hibernation, error correction, etc.) at the root trace level
- Captures lifecycle events within `RuntimeTrace` objects
- Provides a complete timeline of entity state transitions
- Integrates seamlessly with the existing recursive-observer tracing system

## Key Components

### 1. Enhanced RuntimeTrace Model

The `RuntimeTrace` model now includes an optional `lifecycle_events` field:

```python
@dataclass
class RuntimeTrace:
    events: list[tuple[str, int, str]]
    timing: dict[str, float]
    variable_snapshots: list[dict[str, Any]]
    lifecycle_events: list[dict[str, Any]] | None = None  # NEW: Track entity lifecycle
```

### 2. Root Trace Event Recording

New functions in `tracer.py`:

- `record_lifecycle_event()` - Records a lifecycle event at the root trace level
- `get_lifecycle_events()` - Retrieves all recorded lifecycle events
- `clear_lifecycle_events()` - Clears the lifecycle event buffer

### 3. Enhanced EntityLifecycleManager

All lifecycle methods now record events to the root trace:

- `create_entity()` → `entity_created` event
- `awaken_entity()` → `entity_awakening` + `entity_activated` events
- `hibernate_entity()` → `entity_hibernated` event
- `error_correction_mode()` → `entity_error_correction` event
- `offline_adapt()` → `entity_offline_adapt` event
- `quantum_entangle()` → `entity_quantum_entangled` event

## Usage Examples

### Basic Usage

```python
from skills.entity_lifecycle import EntityLifecycleManager
from recursive_observer.tracer import trace_execution, get_lifecycle_events

def my_lifecycle_operations():
    manager = EntityLifecycleManager()
    entity = manager.create_entity('my_entity', 'worker', 'production')
    manager.awaken_entity('my_entity')
    return entity

# Trace the operations
trace = trace_execution(my_lifecycle_operations)

# Access lifecycle events captured in the trace
for event in trace.lifecycle_events:
    print(f"{event['event_type']}: {event['entity_id']} -> {event['state']}")
```

### Detailed Event Inspection

```python
trace = trace_execution(my_lifecycle_operations)

# Examine the timeline of lifecycle events
for event in trace.lifecycle_events:
    timestamp = event['timestamp']
    event_type = event['event_type']
    entity_id = event['entity_id']
    state = event['state']
    metadata = event['metadata']
    
    print(f"[{timestamp}] {event_type}")
    print(f"  Entity: {entity_id}")
    print(f"  State: {state}")
    print(f"  Metadata: {metadata}")
```

### Complete Lifecycle Observability

```python
from recursive_observer.tracer import trace_execution

def complex_lifecycle():
    manager = EntityLifecycleManager()
    
    # Create multiple entities
    e1 = manager.create_entity('entity_alpha', 'observer')
    e2 = manager.create_entity('entity_beta', 'recorder')
    
    # Perform lifecycle operations
    manager.awaken_entity('entity_alpha')
    manager.quantum_entangle('entity_beta', 'quantum_realm')
    manager.awaken_entity('entity_beta')
    manager.hibernate_entity('entity_alpha', depth=2)
    manager.error_correction_mode('entity_beta')
    
    return manager.get_swarm_status()

# Trace everything
trace = trace_execution(complex_lifecycle)

# Now you have:
# - Function call traces (trace.events)
# - Timing information (trace.timing)
# - Variable snapshots (trace.variable_snapshots)
# - Complete lifecycle event timeline (trace.lifecycle_events)
```

## Event Structure

Each lifecycle event has the following structure:

```python
{
    'timestamp': 1770627187.773,  # Unix timestamp
    'event_type': 'entity_created',  # Event type
    'entity_id': 'my_entity',  # Entity identifier
    'state': 'hibernating',  # Entity state
    'metadata': {  # Event-specific metadata
        'role': 'observer',
        'domain': 'consciousness'
    }
}
```

## Event Types

| Event Type | Triggered By | State |
|------------|-------------|-------|
| `entity_created` | `create_entity()` | hibernating |
| `entity_awakening` | `awaken_entity()` | awakening |
| `entity_activated` | `awaken_entity()` | active |
| `entity_hibernated` | `hibernate_entity()` | hibernating |
| `entity_error_correction` | `error_correction_mode()` | error_correction |
| `entity_offline_adapt` | `offline_adapt()` | offline_adapting |
| `entity_quantum_entangled` | `quantum_entangle()` | (current state) |

## Testing

Run the integration tests:

```bash
# Test lifecycle trace integration
python tests/test_lifecycle_trace.py

# Run all recursive-observer tests
cd recursive-observer && pytest tests/ -v
```

## Demonstration

Run the complete demonstration:

```bash
python examples/lifecycle_trace_demo.py
```

This will:
1. Create multiple entities
2. Perform various lifecycle operations
3. Trace all operations
4. Display the complete lifecycle event timeline

## Benefits

1. **Complete Observability**: Every entity lifecycle transition is now traceable
2. **Root Level Integration**: Lifecycle events are captured at the same level as function calls
3. **Unified Tracing**: One `RuntimeTrace` object contains both execution traces and lifecycle events
4. **Minimal Overhead**: Lifecycle recording only adds microseconds to each operation
5. **Backwards Compatible**: Existing code continues to work; lifecycle events are optional

## Architecture

```
┌─────────────────────────────────────────────┐
│   Entity Lifecycle Manager                  │
│   (skills/entity_lifecycle.py)             │
└──────────────┬──────────────────────────────┘
               │ record_lifecycle_event()
               ▼
┌─────────────────────────────────────────────┐
│   Root Trace System                         │
│   (recursive_observer/tracer.py)           │
│                                             │
│   Global: _lifecycle_events                │
└──────────────┬──────────────────────────────┘
               │ included in
               ▼
┌─────────────────────────────────────────────┐
│   RuntimeTrace                              │
│   (recursive_observer/models.py)           │
│                                             │
│   - events                                  │
│   - timing                                  │
│   - variable_snapshots                      │
│   - lifecycle_events  ← NEW                 │
└─────────────────────────────────────────────┘
```

## Implementation Notes

- Lifecycle events are stored in a global list during execution
- `trace_execution()` automatically captures and clears lifecycle events
- The tracer is backwards compatible; `lifecycle_events` can be `None`
- If the tracer module is not available, lifecycle recording silently fails

## Future Enhancements

Potential future improvements:

1. Lifecycle event filtering by entity ID or domain
2. Lifecycle event persistence to disk
3. Real-time lifecycle event streaming
4. Integration with visualization tools
5. Lifecycle event replay functionality
