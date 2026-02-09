# Engine System Documentation

## Overview

The Evez666 engine system provides a complete offline-resilient infrastructure for resource management, trajectory optimization, and provenance tracking. All state is persisted to append-only JSONL files with SHA-256 hash chaining for audit integrity.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ENGINE SYSTEM                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Resource    │  │  Navigation  │  │  Latent      │     │
│  │  Engine      │  │  Mesh        │  │  Cache       │     │
│  │              │  │              │  │              │     │
│  │  • Pools     │  │  • Gates     │  │  • Offline   │     │
│  │  • Scaling   │  │  • Tokens    │  │  • Queue     │     │
│  │  • Health    │  │  • Routes    │  │  • Sync      │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│         ┌──────────────────┴──────────────────┐             │
│         │                                      │             │
│  ┌──────▼───────┐  ┌──────────────┐  ┌───────▼──────┐     │
│  │  Entity      │  │  Metrics     │  │  Trajectory  │     │
│  │  Manager     │  │  Collector   │  │  Optimizer   │     │
│  │              │  │              │  │              │     │
│  │  • States    │  │  • Gauges    │  │  • Beam      │     │
│  │  • Lifecycle │  │  • Meters    │  │  • Score     │     │
│  │  • Recovery  │  │  • Health    │  │  • Fold      │     │
│  └──────────────┘  └──────────────┘  └──────┬───────┘     │
│                                              │             │
│                    ┌──────────────────────────┘             │
│                    │                                        │
│             ┌──────▼───────┐                                │
│             │  Provenance  │                                │
│             │  Domain      │                                │
│             │              │                                │
│             │  • Audit     │                                │
│             │  • Redact    │                                │
│             │  • Anomaly   │                                │
│             └──────────────┘                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Resource Engine (`src/engine/resource_engine.py`)

**Purpose**: Self-running background task processor with priority queue and resource management.

**Features**:
- Resource pools: compute, storage, network, database
- Auto-scaling based on utilization (80% up, 30% down)
- Self-healing with exponential backoff
- Health check system
- State persisted to `src/memory/engine_state.jsonl`

**Usage**:
```python
from engine.resource_engine import ResourceEngine, Task, TaskPriority, ResourceType

engine = ResourceEngine()
engine.start()

task = Task("task_1", TaskPriority.NORMAL, ResourceType.COMPUTE)
engine.submit_task(task)
engine.run_cycle()

status = engine.get_status()
```

**CLI**:
```bash
python execute.py engine
```

### 2. Navigation Mesh (`src/engine/nav_mesh.py`)

**Purpose**: Threshold-based routing with zero-trust gate logic.

**Features**:
- Three domains: Wealth (revenue), Info (data), Myth (content)
- JWT-style token validation per cell/flow
- Anomaly detection (rate spikes, breaches)
- Multi-route paths: primary → failover → offline
- Gate state persisted to `src/memory/gate_log.jsonl`

**Usage**:
```python
from engine.nav_mesh import NavigationMesh, ThresholdDomain

nav = NavigationMesh()
token = nav.issue_token(ThresholdDomain.WEALTH, "user_001")
success, error, route = nav.navigate(ThresholdDomain.WEALTH, token, "user_001")
```

**CLI**:
```bash
python execute.py gate
python execute.py nav
```

### 3. Latent Cache (`src/engine/latent_cache.py`)

**Purpose**: Local-first data store with offline queue and sync.

**Features**:
- JSON file cache (simulating IndexedDB/PouchDB)
- Offline operation queue
- Opportunistic sync when online
- Cache invalidation with TTL
- 100% offline tolerance target

**Usage**:
```python
from engine.latent_cache import LatentCache

cache = LatentCache()
cache.set('key', {'data': 'value'}, ttl=3600)
value = cache.get('key')

# Simulate offline
cache.set_online(False)
cache.set('offline_key', 'data')  # Queued
cache.set_online(True)
cache.sync()  # Syncs queued operations
```

**CLI**:
```bash
python execute.py offline
```

### 4. Entity Manager (`src/engine/entity_manager.py`)

**Purpose**: Entity lifecycle management with state machine.

**Features**:
- States: Hibernating → Awakening → Active → Error Correction → Offline Adapting
- Spawn/hibernate/awaken/deactivate operations
- Health monitoring and auto-recovery
- Entity registry persisted to `src/memory/entities.jsonl`

**Usage**:
```python
from engine.entity_manager import EntityManager, EntityType

manager = EntityManager()
entity = manager.spawn("worker_001", EntityType.WORKER)
manager.awaken("worker_001")
manager.monitor_health()  # Auto-recovery if unhealthy
```

**CLI**:
```bash
python execute.py entity
```

### 5. Metrics Collector (`src/engine/metrics.py`)

**Purpose**: Gauges and meters for system monitoring.

**Gauges** (0-100):
- **Latency Tolerance**: % operations surviving 24h offline
- **Threshold Lock**: Gate breach attempts blocked
- **Resource Flow**: Latent throughput ratio

**Meters** (trend tracking):
- **Nav Velocity**: Path switches per interval
- **Gate Density**: Thresholds enforced

**Usage**:
```python
from engine.metrics import MetricsCollector

metrics = MetricsCollector()
metrics.integrate(resource_engine=engine, nav_mesh=nav, latent_cache=cache)
metrics.update_all()

gauges = metrics.get_all_gauges()
meters = metrics.get_all_meters()
```

### 6. Trajectory Optimizer (`src/engine/trajectory.py`)

**Purpose**: Equitable trajectory optimization with beam search.

**Features**:
- Forward chaining closure generator
- Multi-objective scoring (efficiency + fairness)
- Beam search for optimal path selection
- Fold to canonical hash (spine compression)
- State persisted to `src/memory/trajectory_log.jsonl`

**Usage**:
```python
from engine.trajectory import TrajectoryOptimizer, Fact

optimizer = TrajectoryOptimizer()
optimizer.add_fact('A', True)
optimizer.add_rule('rule1', ['A'], 'B', cost=1.0)

initial_facts = {Fact('A', True)}
best_path = optimizer.beam_search_optimal_spine(initial_facts)
spine_hash = optimizer.fold_to_hash(best_path)
```

**CLI**:
```bash
python execute.py trajectory
```

### 7. Provenance Domain (`src/engine/provenance.py`)

**Purpose**: Observability and audit with safe boundaries.

**Features**:
- Event tap with redaction pipeline
- PII/secret filtering with hashing
- Anomaly detection (rate, drift, bursts)
- Ring buffer for bounded memory
- Provenance graph tracking
- State persisted to `src/memory/provenance_log.jsonl`

**Usage**:
```python
from engine.provenance import ProvenanceDomain

provenance = ProvenanceDomain()
provenance.tap_event('user_action', {'data': 'sensitive@email.com'}, 'run_001')
provenance.add_provenance_edge('fact_A', 'fact_B', 'rule1', 'run_001')

graph = provenance.get_provenance_graph()
audit = provenance.export_audit()
```

**CLI**:
```bash
python execute.py provenance
```

## Hash-Chain Audit

All JSONL logs use SHA-256 hash chaining for tamper-evident audit:

```json
{
  "event_type": "...",
  "timestamp": 1234567890.123,
  "parent_hash": "abc123...",
  "event_hash": "def456...",
  "..."
}
```

**Verification**:
```bash
python audit_log_analyzer.py hashchain
```

## Testing

Run comprehensive test suite:
```bash
python -m pytest tests/test_resource_engine.py -v
```

**Test coverage**:
- Resource pool scaling (up/down)
- Threshold gate validation (block/allow)
- Offline cache queue and sync
- Entity state transitions and recovery
- Hash-chain integrity (all logs)
- Metric gauge calculations
- Trajectory optimization (forward chain, beam search, fold)
- Provenance tracking (PII redaction, anomaly detection)

## Integration with Profit Circuit

The engine system integrates with the existing profit circuit:

```
Orders.jsonl → Revenue Metrics → Resource Engine
           ↓
        Gate Log → Audit Log Analyzer
           ↓
      Entities → Entity Manager → Resource Allocation
```

**Backward compatibility**: All existing profit circuit commands still work:
```bash
python execute.py order    # Create order
python execute.py status   # System status
python execute.py wealth   # Wealth projections
```

## File Structure

```
src/
  engine/
    __init__.py
    resource_engine.py    # Resource pools & auto-scaling
    nav_mesh.py           # Threshold gates & routing
    latent_cache.py       # Offline-first cache
    entity_manager.py     # Entity lifecycle
    metrics.py            # Gauges & meters
    trajectory.py         # Beam search & optimization
    provenance.py         # Audit & observability
  memory/
    engine_state.jsonl    # Resource engine events
    gate_log.jsonl        # Navigation & gate events
    entities.jsonl        # Entity lifecycle events
    trajectory_log.jsonl  # Trajectory optimization events
    provenance_log.jsonl  # Provenance & audit events
    orders.jsonl          # Profit circuit (existing)
    cache/                # Latent cache storage
tests/
  test_resource_engine.py # Comprehensive test suite
execute.py                # CLI interface (updated)
audit_log_analyzer.py     # Log analysis (updated)
```

## Performance Targets

- **Latency Tolerance**: 100% (all critical ops work offline)
- **Threshold Lock**: 95% (gate breach attempts blocked)
- **Resource Flow**: 80% (efficient cache utilization)
- **Hash Chain**: 100% integrity verification
- **Test Coverage**: 22/22 tests passing

## CLI Commands

```bash
# Core engine
python execute.py engine      # Resource engine status
python execute.py gate        # Threshold gate status
python execute.py entity      # Entity registry
python execute.py nav         # Navigation mesh routes
python execute.py offline     # Test 24h offline mode

# Advanced
python execute.py trajectory  # Trajectory optimizer
python execute.py provenance  # Provenance & audit

# Audit
python audit_log_analyzer.py hashchain  # Verify all hash chains
python audit_log_analyzer.py verify     # Full integrity check
```

## Design Principles

1. **Offline-First**: All critical operations work air-gapped
2. **Zero-Trust**: Gate validation at every access point
3. **Append-Only**: Immutable JSONL logs with hash chains
4. **Self-Healing**: Auto-recovery and error correction
5. **Observable**: Full provenance and audit trails
6. **Equitable**: Fair resource allocation and trajectory scoring
7. **Pure Python**: No external dependencies beyond stdlib (except tests)

## Future Extensions

- Symmetry orbit domain (group theory & bundle visualization)
- Phase space domain (Hamiltonian flow & trajectories)
- Action landscape domain (variational optimization)
- Quantum state domain (wavefunction evolution)

## References

- Trajectory optimization: Beam search with fairness weights
- Provenance: W3C PROV-DM standard patterns
- Hash chaining: Bitcoin-style append-only ledger
- Offline-first: CouchDB/PouchDB replication model
