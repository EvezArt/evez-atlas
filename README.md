# Evez666

Evez666 contains working notes and runbooks for controlled, authorized security exercises.

## Features

- **Quantum Threat Detection** - Classical simulation and IBM Quantum integration
- **Autonomous Agent Swarm** - Self-organizing agents with persistent memory
- **Tiered Access Control** - Multi-level API authentication
- **Sacred Memory** - Persistent event logging (events.jsonl)
- **Causal Chain Analysis** - Network threat pattern detection

## Quick Start

### Bootstrap Swarm Infrastructure

```bash
./scripts/swarm-bootstrap.sh
```

### Deploy Services

```bash
./scripts/deploy-all.sh
```

### Check Status

```bash
curl -H "X-API-Key: tier3_director" http://localhost:8000/swarm-status
```

## Documentation

- [Initial Access](docs/initial-access.md)
- [Access Gateway Pipeline](docs/ops/access-gateway.md)
- [Swarm Infrastructure](docs/swarm-infrastructure.md) - Autonomous agent capabilities

## Project Structure

```
Evez666/
├── SOUL.md                  # Agent personality definition
├── scripts/
│   ├── swarm-bootstrap.sh   # Initialize swarm infrastructure
│   └── deploy-all.sh        # Start all services
├── skills/                  # Agent capability modules
│   ├── event_logger.py      # Sacred memory logging
│   ├── swarm.py             # Agent orchestration
│   └── quantum_integration.py # Quantum backend
├── data/
│   └── events.jsonl         # Sacred memory event log
├── src/
│   ├── api/                 # FastAPI server
│   └── tests/               # Test suite
├── quantum.py               # Quantum threat detection
└── demo.py                  # Demo and examples
```

## Testing

Run all tests:

```bash
pytest src/tests/ -v
```

Run swarm-specific tests:

```bash
pytest src/tests/python/test_swarm.py -v
```
