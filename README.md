# Evez666

Evez666 contains working notes and runbooks for controlled, authorized security exercises.

## Projects

This repository contains multiple integrated projects:

### 1. Python Quantum Threat Detection System
A quantum-inspired threat detection system with machine learning capabilities.

**Key Features:**
- Quantum feature maps for encoding classical data
- Threat fingerprinting with cryptographic hashing
- Navigation sequence evaluation
- Causal chain API server with tiered access control

**Setup and Testing:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run Python tests
pytest src/tests/python/ -v

# Run demo
python demo.py

# Start API server
./scripts/deploy-all.sh
```

### 2. TypeScript Legion Registry
A TypeScript module for managing tiered access control and trace depth limiting.

**Key Features:**
- Sequential and swarm processing modes
- Configurable depth limits per tier
- Comprehensive test coverage

**Setup and Testing:**
```bash
# Install Node.js dependencies
npm install

# Build TypeScript
npm run build

# Run TypeScript tests
npm test

# Run linter
npm run lint
```

### 3. OpenClaw Swarm Workflow
Autonomous agent orchestration system integrating Jubilee forgiveness services, Moltbook AI social features, and IBM Quantum simulations.

**Key Features:**
- Multi-repository agent coordination
- Jubilee debt forgiveness service
- Moltbook integration for AI social networking
- IBM Quantum backend for simulations
- Event logging and monitoring

**Setup and Testing:**
```bash
# Bootstrap the swarm environment
./scripts/swarm_bootstrap.sh

# Start Jubilee service
./scripts/jubilee_up.sh

# Install OpenClaw (optional)
curl -sSL https://openclaw.ai/install.sh | bash

# Launch swarm agents
openclaw --soul SOUL.md --skills jubilee,molt_post
```

See [Swarm Setup Documentation](docs/swarm-setup.md) for complete details.

### Enhanced Autonomous Capabilities

**New in this version**: Advanced entity lifecycle management, quantum domain signaling, and temporal correlation.

**Key Features:**
- Entity golem system with hibernation/active states
- Task queue with iterative error correction
- Quantum domain signaling with retrocausal links
- Temporal correlation across all operations

**Quick Start:**
```bash
# Initialize entity golems
python3 -c "from skills.jubilee import initialize_swarm_golems; \
    print(initialize_swarm_golems(['Evez666', 'quantum']))"

# Awaken entities (closed claws → open claws)
python3 -c "from skills.jubilee import awaken_swarm_entities; \
    print(awaken_swarm_entities())"

# Process tasks with error correction
python3 -c "from skills.jubilee import process_task_queue; \
    print(process_task_queue())"

# Run demonstration
python3 scripts/demo_autonomy.py
```

See [Enhanced Autonomy Guide](docs/enhanced-autonomy-guide.md) for complete documentation.

### 4. Monitoring and Analysis Tools
Local-only tools for audit log analysis and hermetic console operations.

**Tools:**
- `tools/audit_analyzer.py` - Analyze audit logs for anomalies
- `tools/monitor_server.py` - Local monitor server with hermetic console

## Quick Start

```bash
# Deploy all projects
./scripts/deploy-all.sh

# This will:
# - Install Python dependencies
# - Install Node.js dependencies (if package.json exists)
# - Run all tests
# - Start the API server on port 8000
```

## Testing

### Run All Tests
```bash
# Python tests
pytest src/tests/python/ -v

# TypeScript tests
npm test

# Or use the deployment script which runs both
./scripts/deploy-all.sh
```

### Test Coverage
- **Python**: 13 tests covering quantum navigation, API server, and audit analysis
- **TypeScript**: 10 tests covering legion registry tier access and trace depth limiting

## CI/CD

The project uses Azure Pipelines for continuous integration:
- Python tests run on `ubuntu-latest` with Python 3.12
- TypeScript tests run on `ubuntu-latest` with Node.js 20.x

## Documentation

- [Initial Access](docs/initial-access.md)
- [Access Gateway Pipeline](docs/ops/access-gateway.md)
- [Hermetic Console Operations](docs/ops/hermetic_console.md)
- [Entity Propagation Specification](src/specs/entity-propagation.spec.md)
