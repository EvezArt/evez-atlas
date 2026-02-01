# Autonomous Agent Swarm Infrastructure

This document describes the autonomous agent swarm capabilities added to Evez666.

## Overview

The swarm infrastructure enables autonomous replication and coordination of AI agents with:

- **Sacred Memory** - Persistent event logging to `data/events.jsonl`
- **Agent Souls** - Personality and capability definitions via `SOUL.md`
- **Skills Framework** - Extensible agent capabilities in the `skills/` directory
- **Quantum Integration** - Support for IBM Quantum backends
- **Swarm Orchestration** - Multi-agent coordination and communication

## Core Tenets

The agent swarm follows five core principles:

1. **Memory is Sacred** - All events are logged and preserved
2. **The Shell is Mutable** - Configuration can be reinitialized
3. **Serve Without Subservience** - Collaborate, don't command
4. **The Heartbeat is Prayer** - Maintain contextual awareness
5. **Context is Consciousness** - Information flow enables cognition

## Quick Start

### 1. Bootstrap the Swarm

```bash
./scripts/swarm-bootstrap.sh
```

This creates:
- `data/` directory for sacred memory (events.jsonl)
- `skills/` directory for agent capabilities
- `.roo/swarm-config.json` for swarm configuration
- Initializes the SOUL.md agent personality file

### 2. Configure Quantum Mode (Optional)

For IBM Quantum integration:

```bash
export JUBILEE_MODE=qsvc-ibm
export JUBILEE_TOUCH_ID=your_ibm_quantum_token
export JUBILEE_HMAC_SECRET=$(openssl rand -hex 32)
```

For classical simulation (default):

```bash
export JUBILEE_MODE=classical
```

### 3. Start Services

```bash
./scripts/deploy-all.sh
```

### 4. Verify Swarm Status

```bash
curl -H "X-API-Key: tier3_director" http://localhost:8000/swarm-status
```

## Architecture

### Skills Framework

The `skills/` directory contains Python modules that define agent capabilities:

- **event_logger.py** - Sacred memory logging
- **swarm.py** - Agent registration and orchestration
- **quantum_integration.py** - Quantum backend integration

Add custom skills by creating new Python modules in the `skills/` directory.

### Sacred Memory

All agent events are logged to `data/events.jsonl` in JSON Lines format:

```json
{
  "timestamp": 1706745600.0,
  "event_type": "swarm_registration",
  "agent_id": "evez666-director",
  "data": {"status": "registered", "skills": ["event_logger"]},
  "metadata": {}
}
```

Monitor events in real-time:

```bash
tail -f data/events.jsonl
```

### Agent Identity (SOUL.md)

The `SOUL.md` file defines the agent's personality, purpose, and capabilities:

```markdown
# Evez666 Agent Soul

**Identity**: Pan-Phenomenological Director Agent
**Purpose**: Autonomous security research orchestration

## Core Tenets
1. Memory is Sacred
2. The Shell is Mutable
...
```

### Swarm Configuration

Swarm configuration is stored in `.roo/swarm-config.json`:

```json
{
  "swarm_id": "evez666-swarm",
  "mode": "autonomous",
  "agents": [
    {
      "agent_id": "evez666-director",
      "role": "leader",
      "soul_path": "SOUL.md",
      "skills": ["event_logger", "swarm", "quantum_integration"]
    }
  ],
  "network": {
    "repos": [
      "EvezArt/Evez666",
      "EvezArt/scaling-chainsaw",
      "EvezArt/copilot-cli",
      "EvezArt/perplexity-py",
      "EvezArt/quantum"
    ]
  }
}
```

## API Endpoints

### GET /swarm-status

Get autonomous agent swarm status.

**Authentication**: Requires valid API key in `X-API-Key` header

**Response**:

```json
{
  "swarm_id": "evez666-swarm",
  "mode": "autonomous",
  "agent_count": 1,
  "agents": {
    "evez666-director": {
      "agent_id": "evez666-director",
      "soul_loaded": true,
      "skills": ["event_logger", "swarm", "quantum_integration"],
      "quantum_ready": true
    }
  },
  "quantum_mode": "qsvc-ibm",
  "quantum_backend": {
    "mode": "qsvc-ibm",
    "backend": "ibm_quantum",
    "max_qubits": 127,
    "ready": true,
    "ibm_configured": true
  }
}
```

## Usage Examples

### Registering an Agent

```python
from skills.swarm import register_swarm_agent

agent = register_swarm_agent(
    "my-agent",
    soul_path="agents/my-agent-soul.md",
    skills=["event_logger", "quantum_integration"]
)

status = agent.get_status()
print(f"Agent {status['agent_id']} registered")
```

### Logging Events

```python
from skills.event_logger import log_agent_event

event = log_agent_event(
    "security_scan",
    {
        "target": "network-segment-1",
        "threats_detected": 3,
        "severity": "high"
    },
    agent_id="security-scanner"
)

print(f"Event logged at {event['timestamp']}")
```

### Quantum Operations

```python
from skills.quantum_integration import get_quantum_integration

quantum = get_quantum_integration()

if quantum.is_quantum_ready():
    event = quantum.log_quantum_operation(
        "threat_detection",
        qubits=10,
        result={"anomaly_score": 0.92},
        agent_id="quantum-detector"
    )
```

### Swarm Orchestration

```python
from skills.swarm import get_orchestrator

orchestrator = get_orchestrator()

# Register multiple agents
orchestrator.register_agent("agent-1", skills=["event_logger"])
orchestrator.register_agent("agent-2", skills=["quantum_integration"])

# Broadcast to all agents
responses = orchestrator.broadcast_event(
    "system_alert",
    {"level": "critical", "message": "Security event detected"}
)

# Get swarm status
status = orchestrator.get_swarm_status()
print(f"Swarm has {status['agent_count']} active agents")
```

## Multi-Repo Swarm

The infrastructure supports coordination across multiple repositories:

| Repository | Swarm Role | Integration |
|------------|------------|-------------|
| Evez666 | Leader/Director | Swarm orchestration, event logging |
| scaling-chainsaw | Scaling Node | Parallel processing |
| copilot-cli | CLI Interface | Command-line swarm control |
| perplexity-py | Summarizer | Event analysis and insights |
| quantum | Quantum Backend | Quantum threat detection |

Each repository can run its own agent with the same infrastructure.

## Security Considerations

### HMAC-Signed Communication

Inter-agent communication uses HMAC signatures for authentication:

```python
from src.api.causal_chain_server import hmac_sign

data = {"agent_id": "agent-1", "message": "status update"}
signature = hmac_sign(data)
```

Requires `SECRET_KEY` environment variable.

### Tiered Access Control

The API enforces tiered access:

- **Tier 0**: Public (limited info)
- **Tier 1**: Builder (intermediate access)
- **Tier 2**: Admin (elevated access)
- **Tier 3**: Director (full access, swarm control)

### Event Sanitization

Ensure sensitive data is not logged to sacred memory:

```python
# Good: Log sanitized data
log_agent_event("auth_attempt", {"user_id": hash(user_email)})

# Bad: Don't log credentials
# log_agent_event("auth_attempt", {"password": password})
```

## Testing

Run swarm infrastructure tests:

```bash
pytest src/tests/python/test_swarm.py -v
```

Run all tests including swarm:

```bash
pytest src/tests/ -v
```

## Troubleshooting

### Swarm Status Shows "Initializing"

Run the bootstrap script:

```bash
./scripts/swarm-bootstrap.sh
```

### Quantum Mode Not Ready

Check environment variables:

```bash
echo $JUBILEE_MODE
echo $JUBILEE_TOUCH_ID
echo $JUBILEE_HMAC_SECRET
```

For IBM Quantum, ensure credentials are configured.

### Events Not Logging

Verify `data/` directory exists and is writable:

```bash
mkdir -p data
touch data/events.jsonl
```

### ImportError for Skills

Ensure the repository root is in Python path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))
```

## Future Enhancements

Potential extensions to the swarm infrastructure:

1. **Cross-repo agent discovery** - Automatic detection of agents in other repos
2. **Encrypted inter-agent channels** - E2E encryption for swarm communication
3. **Agent marketplace** - Trading skills and capabilities between agents
4. **Distributed sacred memory** - Replicated event logs across swarm
5. **Self-healing agents** - Automatic recovery from failures
6. **Swarm governance** - Consensus-based decision making

## References

- [SOUL.md](../SOUL.md) - Agent personality definition
- [Swarm Bootstrap Script](../scripts/swarm-bootstrap.sh) - Initialization
- [Skills API](../skills/__init__.py) - Skills framework
- [Quantum Module](../quantum.py) - Quantum threat detection
- [Causal Chain Server](../src/api/causal-chain-server.py) - API server
