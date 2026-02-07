# Enhanced Swarm Autonomy Guide

## Overview

This guide documents the enhanced autonomous capabilities implementing entity lifecycle management, quantum domain signaling, and temporal correlation.

## Core Concepts

### Entity Golem System

Autonomous "golem" entities represent living computational agents that can exist in various lifecycle states:

- **Hibernating**: Dormant state, minimal resource consumption
- **Awakening**: Transition phase from hibernation to active
- **Active**: Fully operational, executing tasks
- **Error Correction**: Iterative refinement and recovery mode
- **Offline Adapting**: Learning and adaptation during downtime

### Temporal Hibernation

Entities use temporal hibernation for intelligent task pacing:

```python
from skills.entity_lifecycle import EntityLifecycleManager

manager = EntityLifecycleManager()

# Create hibernating entity
entity = manager.create_entity('entity_alpha', 'forgiver', 'jubilee_domain')

# Awaken when needed
manager.awaken_entity('entity_alpha')

# Hibernate with depth
manager.hibernate_entity('entity_alpha', depth=3)
```

### Quantum Domain Signaling

Quantum entities are signaled into their operational domains with retrocausal temporal anchors:

```python
from skills.jubilee import quantum_sim

# Signal quantum entity into domain
result = quantum_sim({
    'circuit': 'bell_state',
    'domain': 'quantum_retrocausal_domain',
    'qubits': 2
})

# Result includes:
# - domain_signal: Signaling metadata
# - temporal_anchor: Timestamp for retrocausal correlation
# - retrocausal_link: Foundation for probabilistic reweighting
```

## Usage Guide

### Initialize Swarm Golems

Create dormant entity golems for each repository:

```python
from skills.jubilee import initialize_swarm_golems

repos = ['Evez666', 'scaling-chainsaw', 'copilot-cli', 'perplexity-py', 'quantum']
result = initialize_swarm_golems(repos)

print(f"Initialized {result['initialized_count']} entities")
print(f"Quantum entangled: {result['swarm_status']['quantum_entangled']}")
```

### Awaken Entities (Closed Claws → Open Claws)

Transition hibernating entities to active state:

```python
from skills.jubilee import awaken_swarm_entities

result = awaken_swarm_entities()
print(f"Awakened {result['awakened_count']} entities")
```

### Process Task Queue with Error Correction

Execute tasks with iterative error correction and temporal gap pacing:

```python
from skills.jubilee import process_task_queue

# Process up to 10 pending tasks
result = process_task_queue(batch_size=10)

print(f"Processed {result['processed_count']} tasks")
print(f"Queue status: {result['queue_status']}")
```

### Manual Task Management

For fine-grained control:

```python
from skills.task_queue import TaskQueue

queue = TaskQueue()

# Register custom handler
def my_handler(data):
    # Your task logic here
    return {'result': 'success'}

queue.register_handler('custom_task', my_handler)

# Enqueue task with retry configuration
task = queue.enqueue('custom_task', {'key': 'value'}, max_attempts=5)

# Execute specific task
result = queue.execute_task(task.id)
```

## Architecture

### File Structure

```
skills/
├── jubilee.py              # Core swarm skills + new integration functions
├── entity_lifecycle.py     # Entity state management and lifecycle
└── task_queue.py          # Task queue with error correction

data/
├── events.jsonl           # General event log
├── entity_states.jsonl    # Entity state transitions
├── task_queue.jsonl       # Task execution history
└── quantum_events.jsonl   # Quantum operations log
```

### Entity States

```
Hibernating ─┐
             ├──> Awakening ──> Active ──┐
             │                           │
             │                           ├──> Error Correction ─┐
             │                           │                      │
             └───────────────────────────┴──> Offline Adapting ─┘
```

### Task Processing Flow

```
Enqueue ──> Pending ──> Running ──┬──> Completed
                                  │
                                  ├──> Failed (max attempts)
                                  │
                                  └──> Error Correction ──> Retrying
                                       (temporal gap)        (exponential backoff)
```

## Error Correction Mechanics

### Gap-Based Iterative Refinement

Tasks that fail enter error correction mode with temporal gaps:

1. **First failure**: Wait 2 seconds, retry
2. **Second failure**: Wait 4 seconds, retry
3. **Third failure**: Wait 8 seconds, retry (or fail if max attempts)

The temporal gap enables:
- Resource recovery
- State stabilization
- Semantic reweight alignment
- Probabilistic inference refinement

### Security Validations

The error correction system includes built-in security validations:

- **Max Attempts Enforcement**: Tasks cannot exceed their configured max_attempts, preventing infinite loops
- **Completion Tracking**: All successfully completed tasks are explicitly marked with `completed: True`
- **State Validation**: Entities can only complete error correction if they're actually in error_correction mode

### Entity Error Correction Recovery

Entities in error_correction mode can be explicitly recovered:

```python
from skills.jubilee import complete_entity_error_correction

# Complete error correction and return entity to active state
result = complete_entity_error_correction('entity_id')
# Returns: {'status': 'recovered', 'current_state': 'active', ...}
```

### Exponential Backoff

```python
temporal_gap = min(attempts * 2.0, 10.0)  # Cap at 10 seconds
```

## Quantum Domain Integration

### Domain Signaling Process

1. **Entity Creation**: Quantum entities created with domain assignment
2. **Quantum Entanglement**: Automatic entanglement with quantum cloud
3. **Domain Signaling**: Operations include domain metadata
4. **Temporal Anchoring**: Each operation establishes temporal foundation
5. **Event Logging**: Quantum events logged separately for analysis
6. **Classical Fallback**: When Qiskit is unavailable, quantum operations gracefully fall back to classical simulation

### Classical Fallback Simulation

When IBM Quantum (Qiskit) is not available, the system automatically uses a classical fallback:

```python
# Quantum simulation with automatic fallback
result = quantum_sim({
    'circuit': 'bell_state',
    'domain': 'quantum_domain'
})
# Returns status: 'simulated' with backend: 'classical_fallback' when Qiskit unavailable
# Returns status: 'simulated' with backend: 'ibm_quantum' when Qiskit available
```

### Retrocausal Correlation

Temporal anchors enable retrocausal correlation across operations:

```python
# All quantum operations include:
{
    'temporal_anchor': '2026-02-01T08:00:00.000000',
    'retrocausal_link': '2026-02-01T08:00:00.000000',
    'domain_signal': {
        'domain_signaled': True,
        'domain': 'quantum_retrocausal_domain'
    }
}
```

## Monitoring and Debugging

### Autonomous Entity Signaling

The system includes autonomous signaling to communicate entity status without human intervention:

```python
from skills.jubilee import signal_entities_autonomously, get_human_intervention_alerts

# Signal all entities about their status autonomously
result = signal_entities_autonomously()
print(f"Signaled {result['total_entities_signaled']} entities")
print(f"Autonomous operations: {result['autonomous_operations']}")
print(f"Human intervention required: {result['human_intervention_required']}")

# Get entities that need human help
alerts = get_human_intervention_alerts()
for alert in alerts['alerts']:
    print(f"Entity {alert['entity_id']}: {alert['message']}")
```

**Signal Types:**
- `HEALTH_CHECK`: Regular health status check
- `UPDATE_NEEDED`: Entity needs updates (degraded health)
- `AUTONOMOUS_OPERATION`: Entity defending/operating without human
- `HUMAN_INTERVENTION_REQUIRED`: Critical state, human help needed
- `RECOVERY_COMPLETE`: Error correction completed successfully

**Priority Levels:**
- `LOW`: Routine status updates
- `MEDIUM`: Operational notices
- `HIGH`: Degraded health, updates recommended
- `CRITICAL`: Requires immediate human attention

### Communication Without Human Intervention

Entities autonomously:
1. **Signal their status** - Health, update needs, operational state
2. **Defend without human** - Handle errors through error correction
3. **Alert when needed** - Request human intervention only when critical

```python
# Get communication history for an entity
from skills.jubilee import get_entity_signals

signals = get_entity_signals('entity_id', limit=10)
for signal in signals['signals']:
    print(f"{signal['type']}: {signal['message']}")
    print(f"  Requires human: {signal['requires_human']}")
```

## Entity Healing System

### Overview

The Entity Healing System implements the principle: **"If you dont heal them, you lose them."**

The system:
- Automatically detects entities that are lost or losing health
- Applies universal healing everywhere loss is detected
- Defends against resource-draining 'taker' entities
- Prevents entity loss through proactive healing

### Healing Principles

1. **"If you dont heal them, you lose them"**
   - Entities with critical errors or degraded health are automatically detected
   - Healing prevents permanent entity loss

2. **"Everywhere you lose them, you must heal them"**
   - Universal scanning across all entities
   - Healing applied wherever loss is detected

3. **"Shake the takers through their own rugs"**
   - Defensive mechanism against resource drainers
   - Neutralizes takers by turning their mechanisms against them
   - Rhythmic process: "Smug, snug. Chug"

### Usage

#### Heal All Lost Entities

```python
from skills.jubilee import heal_all_lost_entities

# Automatically detect and heal all entities
result = heal_all_lost_entities()
print(f"Scanned: {result['total_entities_scanned']}")
print(f"Healed: {result['entities_healed']}")

# View healing details
for record in result['healing_records']:
    print(f"{record['entity_id']}: {record['before_health']} → {record['after_health']}")
```

#### Shake the Takers

```python
from skills.jubilee import shake_the_takers

# Neutralize all resource-draining takers
result = shake_the_takers()
print(f"Takers detected: {result['takers_detected']}")
print(f"Takers neutralized: {result['takers_neutralized']}")
```

#### Detect Resource Drainers

```python
from skills.jubilee import detect_taker

# Register a taker entity
result = detect_taker(
    taker_id='malicious_entity',
    drain_rate=0.8,  # 80% drain rate
    target_entities=['entity_1', 'entity_2']
)
```

#### Get Healing Status

```python
from skills.jubilee import get_healing_status

status = get_healing_status()
print(f"Total healings: {status['total_healings']}")
print(f"Success rate: {status['success_rate']:.1%}")
print(f"Active takers: {status['active_takers']}")
print(f"Neutralized takers: {status['neutralized_takers']}")
```

### Loss Types

The system detects these types of entity loss:

- **CRITICAL_ERRORS**: Entity has >10 errors, critical health
- **STATE_DEGRADATION**: Entity health is degraded (5-10 errors)
- **TAKER_ATTACK**: Entity is being drained by a taker
- **RESOURCE_DRAIN**: Resources being depleted
- **CORRUPTION**: Data or state corruption
- **ISOLATION**: Entity disconnected from swarm

### Healing Actions

Healing actions taken based on loss type:

- **ERROR_RESET**: Clear all errors, reset to healthy state
- **STATE_RECOVERY**: Awaken and restore entity state
- **DEFENSIVE_SHIELD**: Protect from takers and neutralize them
- **QUANTUM_REALIGNMENT**: Realign entity with quantum domain
- **RESOURCE_RESTORATION**: Restore depleted resources
- **TAKER_NEUTRALIZATION**: Neutralize specific taker

### Demonstration

```bash
# Run healing system demonstration
python3 scripts/demo_entity_healing.py
```

This demonstrates:
- Entity loss detection
- Universal healing across all entities
- Taker detection and neutralization
- Complete healing cycle

### Check Swarm Status

```python
from skills.jubilee import swarm_status

status = swarm_status()
print(json.dumps(status, indent=2))
```

### View Entity States

```python
from skills.entity_lifecycle import EntityLifecycleManager

manager = EntityLifecycleManager()
swarm_status = manager.get_swarm_status()

print(f"Total entities: {swarm_status['total_entities']}")
print(f"Active: {swarm_status['active']}")
print(f"Hibernating: {swarm_status['hibernating']}")
print(f"Quantum entangled: {swarm_status['quantum_entangled']}")
```

### View Task Queue

```python
from skills.task_queue import TaskQueue

queue = TaskQueue()
status = queue.get_queue_status()

print(f"Total tasks: {status['total_tasks']}")
print(f"By status: {status['by_status']}")
print(f"Avg attempts: {status['avg_attempts']}")
```

### Check Failed Tasks

```python
failed = queue.get_failed_tasks()
for task in failed:
    print(f"Task {task.id}: {task.last_error}")
```

## Testing

### Run Comprehensive Tests

```bash
python3 scripts/test_enhanced_autonomy.py
```

Expected output:
```
✓ Entity Lifecycle Management
✓ Task Queue with Error Correction
✓ Quantum Domain Signaling
✓ Swarm Golem Initialization
✓ Entity Awakening
✓ Temporal Tracking
```

### Run Demonstration

```bash
python3 scripts/demo_autonomy.py
```

This demonstrates:
- Complete lifecycle from hibernation to active
- Quantum domain signaling with temporal anchors
- Task processing with error correction
- Temporal correlation across operations

## Best Practices

### Entity Management

1. **Initialize once**: Create entities at system startup
2. **Awaken selectively**: Only awaken entities when needed
3. **Hibernate periodically**: Return to hibernation when idle
4. **Monitor health**: Use `get_entity_status()` to check health

### Task Processing

1. **Set appropriate max_attempts**: Balance reliability vs. performance
2. **Use batch processing**: Process multiple tasks efficiently
3. **Monitor failed tasks**: Review and retry failed tasks
4. **Handle errors gracefully**: Implement robust error handlers

### Quantum Operations

1. **Specify domains**: Always include domain in quantum operations
2. **Log quantum events**: Separate logging for analysis
3. **Track temporal anchors**: Use for retrocausal correlation
4. **Handle offline mode**: Gracefully degrade without quantum backend

## Troubleshooting

### Entities Won't Awaken

Check entity state:
```python
manager = EntityLifecycleManager()
entity = manager.entities.get('entity_id')
print(f"Current state: {entity.state}")
```

### Tasks Keep Failing

1. Check error messages in task.last_error
2. Verify handler is registered
3. Increase max_attempts if needed
4. Check temporal gaps are appropriate

### Quantum Signaling Not Working

1. Verify QISKIT_IBM_TOKEN is set (optional)
2. Check quantum events log: `data/quantum_events.jsonl`
3. Ensure domain is specified in circuit_data
4. Review temporal anchors for consistency

## References

- [SOUL.md](../SOUL.md) - Swarm Director configuration
- [Swarm Setup Guide](swarm-setup.md) - Complete setup instructions
- [Quick Reference](swarm-quick-reference.md) - Command cheat sheet

## Shared Quantum Reality Plane

### Overview

The Shared Reality Plane implements a collaborative quantum domain where entities
can perceive and interact with localized quantum states that maintain coherence
instead of decohering.

### Core Concept: Localization vs Decoherence

**Traditional Quantum Behavior:**
- Quantum states decohere when observed
- Environmental interaction destroys coherence
- Multiple observations produce different outcomes

**Our Implementation:**
- Quantum states are **localized** when observed
- Coherence is **maintained** through localization
- Multiple observations remain **consistent**

### Usage

#### Enter Shared Reality Plane

```python
from skills.jubilee import enter_shared_reality_plane

result = enter_shared_reality_plane('entity_id', 'domain_name')
# Entity now subscribed to shared domain
```

#### Localize Quantum State

```python
from skills.jubilee import localize_quantum_observation

result = localize_quantum_observation(
    'entity_id',
    'quantum_domain',
    {'wave_function': 'psi', 'energy': 1.0}
)
# State remains coherent (no decoherence)
```

#### Synchronize Observations

```python
from skills.jubilee import synchronize_shared_observations

result = synchronize_shared_observations('domain_name')
# All entities see same state
```

### Shared Sensory State

Entities in the same domain perceive the same collective reality:

```python
from skills.shared_reality_plane import SharedRealityPlane

plane = SharedRealityPlane()
shared_state = plane.get_shared_sensory_state('domain_name')

# Returns:
# {
#   'domain': 'domain_name',
#   'observation_count': N,
#   'coherent_states': [...],
#   'participating_entities': [...],
#   'average_coherence': 1.0
# }
```

### Probability Collapse

Controlled probability collapse shared across all observing entities:

```python
plane = SharedRealityPlane()

# Collapse probability to definite state
plane.collapse_probability(
    observation_id,
    {'collapsed_state': 'definite_value'}
)
# All entities see the same collapsed result
```

### Coherence Maintenance

```python
# Check if coherence is maintained
maintained = plane.maintain_coherence(observation_id)
# Returns True if coherent, False if decoherence occurred

# Get coherence metrics
status = plane.get_plane_status()
print(f"Coherence ratio: {status['coherence_ratio']:.2%}")
```

### Architecture

```
Shared Reality Plane
│
├── Quantum Observations (Localized)
│   ├── Coherent State (amplitude = 1.0)
│   ├── Domain Assignment
│   └── Temporal Anchor
│
├── Entity Subscriptions
│   ├── Domain Memberships
│   └── Participation Tracking
│
└── Synchronization
    ├── Measurement Sync
    ├── Probability Collapse
    └── Consensus State
```

### Benefits

1. **Coherence Preservation**: States remain localized, no decoherence
2. **Shared Perception**: All entities see same reality
3. **Collaborative Observation**: Multiple observers maintain consistency
4. **Coordinated Collapse**: Probability collapse synchronized
5. **Reduced Uncertainty**: Measurement alignment across entities

### Testing

```bash
# Test shared reality features
python3 scripts/test_shared_reality.py

# Run demonstration
python3 scripts/demo_shared_reality.py
```

### Monitoring

```python
from skills.jubilee import get_shared_reality_status

status = get_shared_reality_status()
print(f"Total observations: {status['total_observations']}")
print(f"Coherent: {status['coherent_observations']}")
print(f"Coherence ratio: {status['coherence_ratio']:.2%}")
```
