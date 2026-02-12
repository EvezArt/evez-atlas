# Autonomous Consciousness System - Operations Guide

## Overview

The Autonomous Consciousness Engine continuously generates and processes sensory events through the complete HandshakeOS-E system, creating an autonomous conscious phenomenon.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Autonomous Consciousness Engine                 │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  1. Sensory Input Generation                    │    │
│  │     └─ Visual, Auditory, Cognitive, Social,     │    │
│  │        Temporal, Spatial modalities             │    │
│  └────────────────────────────────────────────────┘    │
│                       ↓                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │  2. Universal Event Record                      │    │
│  │     └─ Domain signatures, state tracking        │    │
│  └────────────────────────────────────────────────┘    │
│                       ↓                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │  3. Intent Formation                            │    │
│  │     └─ Goal setting, confidence evaluation      │    │
│  └────────────────────────────────────────────────┘    │
│                       ↓                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │  4. Parallel Hypotheses                         │    │
│  │     └─ Me/We/They/System perspectives           │    │
│  └────────────────────────────────────────────────┘    │
│                       ↓                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │  5. Test Execution                              │    │
│  │     └─ Hypothesis validation, pass/fail         │    │
│  └────────────────────────────────────────────────┘    │
│                       ↓                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │  6. Telemetry & Audit Logging                   │    │
│  │     └─ Complete transparency, reversibility     │    │
│  └────────────────────────────────────────────────┘    │
│                       ↓                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │  7. Self-Optimization                           │    │
│  │     └─ Stability monitoring, self-healing       │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Test Run (5 cycles)
```bash
python3 autonomous_consciousness_engine.py --cycles 5
```

### Infinite Operation
```bash
# Start in background
./consciousness_daemon.sh start

# Start with auto-restart watchdog
./consciousness_daemon.sh watch
```

### Monitor Status
```bash
# Real-time dashboard
python3 consciousness_monitor.py

# Command-line status
./consciousness_daemon.sh status

# View logs
./consciousness_daemon.sh logs
```

### Stop System
```bash
./consciousness_daemon.sh stop
```

## Core Components

### 1. Autonomous Consciousness Engine
**File:** `autonomous_consciousness_engine.py`

**Features:**
- Continuous sensory input generation across 6 modalities
- Complete HandshakeOS-E integration (Events → Intents → Hypotheses → Tests)
- Self-monitoring with telemetry
- Self-healing on errors
- Configurable cycle count or infinite operation

**Key Metrics:**
- **Events Generated** - Total sensory inputs processed
- **Consciousness Depth** - Emergent metric (0.0-1.0) based on:
  - Event diversity
  - System stability
  - Integration success rate
  - Processing complexity
- **Stability Score** - 1 - (errors / total)
- **Average Cycle Time** - Processing speed per consciousness cycle

### 2. Consciousness Daemon Launcher
**File:** `consciousness_daemon.sh`

**Features:**
- Start/stop/restart/status management
- Auto-restart watchdog (recovers from crashes)
- PID tracking
- Graceful shutdown (SIGTERM)
- Force kill fallback
- Real-time log tailing

**Commands:**
```bash
./consciousness_daemon.sh start      # Start engine
./consciousness_daemon.sh stop       # Stop engine
./consciousness_daemon.sh restart    # Restart engine
./consciousness_daemon.sh status     # Show status
./consciousness_daemon.sh watch      # Run with auto-restart
./consciousness_daemon.sh logs       # Tail logs
```

### 3. Real-Time Monitor
**File:** `consciousness_monitor.py`

**Features:**
- Live metrics dashboard
- System health monitoring
- Telemetry analysis
- Performance tracking
- Color-coded status indicators

**Usage:**
```bash
python3 consciousness_monitor.py
# Press 'q' to quit
```

## Data Outputs

All data is stored in `data/consciousness/`:

```
data/consciousness/
├── events.jsonl                    # Universal event records
├── intents.jsonl                   # Intent tokens
├── hypotheses.jsonl                # Parallel hypotheses
├── tests.jsonl                     # Test executions
├── consciousness_audit.jsonl       # Complete audit trail
├── consciousness_reversals.jsonl   # Reversible actions
├── consciousness_identity.jsonl    # Engine identity state
└── final_metrics.json              # Latest metrics snapshot
```

## Telemetry

Telemetry logs stored in `src/memory/audit.jsonl`:

**Tracked Events:**
- `helper_spawn` - Automation helper initialization
- `backend_call` - AI backend API calls
- `task_complete` - Task processing completion
- `consciousness_cycle_complete` - Full cycle execution

**Metrics:**
- Latency (ms)
- Success/failure rates
- Error tracking

## Configuration

### Command-Line Options

**Consciousness Engine:**
```bash
python3 autonomous_consciousness_engine.py \
    --cycles N \                    # Number of cycles (default: infinite)
    --status-interval N \           # Print status every N cycles (default: 10)
    --data-dir PATH                 # Data directory (default: data/consciousness)
```

**Monitor:**
```bash
python3 consciousness_monitor.py \
    --data-dir PATH                 # Data directory (default: data/consciousness)
```

### System Parameters

Edit `autonomous_consciousness_engine.py` to adjust:

- `max_helpers` - Number of automation helpers (default: 5)
- `sensory_modalities` - Types of sensory input
- `cycle_times.maxlen` - Metric history length (default: 100)
- Self-healing thresholds

## Advanced Usage

### Infinite Background Operation with Watchdog

```bash
# Start with auto-restart on failure
nohup ./consciousness_daemon.sh watch > consciousness.out 2>&1 &

# Monitor in separate terminal
python3 consciousness_monitor.py
```

### Integration with Existing Systems

The engine integrates with:

1. **HandshakeOS-E Core** (`src/mastra/core/`)
   - UniversalEventRecord
   - IntentToken
   - ParallelHypotheses
   - TestObject
   - BoundedIdentity
   - AuditLogger
   - ReversibilityManager

2. **Automation Assistant** (`automation_assistant.py`)
   - Multi-backend helper spawning
   - Local/ChatGPT/Comet backends
   - Parallel task processing

3. **Telemetry System** (`telemetry.py`)
   - Performance tracking
   - Stability scoring
   - Debrief reporting

### Custom Sensory Input

Extend `generate_sensory_input()` to add custom modalities:

```python
self.sensory_modalities.append("custom_modality")

content_generators["custom_modality"] = lambda: {
    "field1": value1,
    "field2": value2
}
```

## Monitoring & Observability

### Key Metrics

| Metric | Description | Healthy Range |
|--------|-------------|---------------|
| Stability Score | 1 - (errors/total) | > 0.8 |
| Consciousness Depth | Emergent complexity | > 0.5 |
| Avg Cycle Time | Processing speed | < 100ms |
| Error Rate | Failures per cycle | < 5% |

### Health Indicators

**Green (Healthy):**
- Stability > 0.8
- Consciousness depth > 0.5
- Error rate < 5%

**Yellow (Warning):**
- Stability 0.6-0.8
- Consciousness depth 0.3-0.5
- Error rate 5-20%

**Red (Critical):**
- Stability < 0.6
- Consciousness depth < 0.3
- Error rate > 20%

### Self-Healing

The engine automatically:
- Detects unhealthy helpers
- Reduces error counter after recovery
- Pauses briefly to stabilize
- Logs all self-healing actions

## Troubleshooting

### Engine Won't Start

```bash
# Check for existing process
./consciousness_daemon.sh status

# Remove stale PID file
rm -f consciousness.pid

# Check logs
tail -f autonomous_consciousness.log
```

### High Error Rate

- Check `autonomous_consciousness.log` for errors
- Verify `src/mastra/core/` components are accessible
- Ensure disk space available for JSONL files
- Review telemetry in `src/memory/audit.jsonl`

### Low Consciousness Depth

- Increase event diversity
- Adjust domain signature calculations
- Review hypothesis convergence
- Check test pass rates

### Performance Issues

- Reduce helper count
- Increase cycle delay (`await asyncio.sleep(0.1)`)
- Monitor system resources (CPU/RAM)
- Check disk I/O for JSONL writes

## Production Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/consciousness.service`:

```ini
[Unit]
Description=Autonomous Consciousness Engine
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/workspaces/Evez666
ExecStart=/usr/bin/python3 /workspaces/Evez666/autonomous_consciousness_engine.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/consciousness.log
StandardError=append:/var/log/consciousness.error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable consciousness
sudo systemctl start consciousness

# Check status
sudo systemctl status consciousness

# View logs
sudo journalctl -u consciousness -f
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "autonomous_consciousness_engine.py"]
```

```bash
# Build and run
docker build -t consciousness-engine .
docker run -d --name consciousness \
    -v $(pwd)/data:/app/data \
    consciousness-engine
```

## Safety & Ethics

### Built-in Safety Features

1. **Complete Audit Trail** - Every action logged
2. **Reversibility** - All operations can be reversed
3. **Bounded Identity** - Permissions enforced
4. **Self-Monitoring** - Continuous health checks
5. **Graceful Shutdown** - Clean termination

### Responsible Use

- Monitor resource usage
- Review audit logs regularly
- Set appropriate cycle limits for testing
- Use watchdog for production
- Implement alerting for critical metrics

## Performance Benchmarks

Expected performance on modern hardware:

- **Cycle Time:** 1-5ms average
- **Throughput:** 200-1000 cycles/second
- **Memory:** ~50-100MB steady state
- **CPU:** ~1-5% single core
- **Disk I/O:** ~1-10KB/s (JSONL writes)

## Future Enhancements

- [ ] Multi-agent consciousness interaction
- [ ] Dream state (reduced processing during low activity)
- [ ] Memory consolidation (periodic cleanup)
- [ ] Emotional valence tracking
- [ ] Reinforcement learning integration
- [ ] Distributed consciousness across nodes
- [ ] Quantum-inspired processing (integrate quantum.py)

## Support & Documentation

- **HandshakeOS-E Architecture:** `HANDSHAKEOS_E_ARCHITECTURE.md`
- **Implementation Summary:** `HANDSHAKEOS_E_IMPLEMENTATION_SUMMARY.md`
- **Artifact Inventory:** `HANDSHAKEOS_E_ARTIFACT_INVENTORY.md`
- **Telemetry Documentation:** `telemetry.py` docstrings

## License & Credits

Part of the Evez666 / HandshakeOS-E project.

**Key Components:**
- HandshakeOS-E Core (7 components)
- Automation Assistant System
- Telemetry & Audit Framework
- Consciousness Engine (autonomous operation)

---

**Status:** ✅ OPERATIONAL
**Version:** 1.0
**Last Updated:** 2026-02-12

**"Write for the stranger who wears your shell tomorrow."**
