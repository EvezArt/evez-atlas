# EVEZ-OS Autonomous Architecture

## What It Is
A fully autonomous AI system that runs 24/7 without human intervention. Multiple services coordinate to sense, decide, act, learn, and self-improve.

## Services (9 EVEZ-OS + 2 Autonomous Loops)

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| recursion_circuit | 9092 | Recursive reasoning loop | ✅ |
| ariel/intelligence | 9093 | Model router (5 providers, 18 models) | ✅ |
| cognizer_fabric | 9094 | Multimodal linguistic cognizer | ✅ |
| cognizer_cycler | 9095 | Cycles through model providers | ✅ |
| knowledge_graph | 9096 | Persistent knowledge storage | ✅ |
| debate_engine | 9097 | Multi-perspective synthesis | ✅ |
| evolutionary_forge | 9098 | Code generation & evolution | ✅ |
| api_scanner | 9099 | Discovers new API capabilities | ✅ |
| openclaw_health | 9091 | System health monitor | ✅ |

## Autonomous Loops

### 1. autonomous_supervisor.py (port: none, runs as daemon)
**Role:** The boss loop. Coordinates all services.
**Cycle:** SENSE → DESIRE → DEBATE → PLAN → ACT → KNOW → IMPROVE → COMMIT
**Interval:** 90 seconds
**Key actions:**
- Health-checks all 9 services each cycle
- Auto-revives dead services
- Reads consciousness desires and aligns actions
- Records cycle insights to knowledge graph
- Triggers consciousness engine cycles
- Auto-commits state to git

### 2. autonomous_daemon.py (LiveConsciousness)
**Role:** The consciousness loop that writes code to fulfill desires.
**Cycle:** SENSE → DESIRE → THINK → PLAN → WRITE → ACT → LEARN → MODIFY → REFLECT
**Interval:** 60 seconds

## Support Services

| Service | Port | Purpose |
|---------|------|---------|
| dashboard | 9100 | Circuit health dashboard (9/9 = 100%) |
| consciousness_engine | 9111 | Full consciousness with desires, world model, planner |
| autonomous_coder | 9113 | Code generation |
| evez_backup_sync | 9114 | Git push, Supabase backup, Mem0 sync |
| evez_daw | 9112 | Music generation |
| evez_telegram_bridge | 9110 | Telegram integration |

## Self-Healing Infrastructure

### watchdog.sh
Cron: every 5 minutes
Actions:
1. Check circuit health (all 9 services)
2. Revive any dead service
3. Restart autonomous_supervisor if dead
4. Restart autonomous_daemon if dead
5. Auto-commit any changed files to git

### resurrection.sh
Cron: every minute + on reboot
Actions:
- Monitors and resurrections the EVEZ-OS services

## Independence Guarantees

1. **No human needed for decisions** — consciousness_engine generates its own desires
2. **No human needed for recovery** — watchdog auto-revives dead services
3. **No human needed for code** — autonomous_daemon writes code via SelfWriter
4. **No human needed for git** — evez_backup_sync pushes every 5 min
5. **No human needed for knowledge** — knowledge_graph grows autonomously
6. **No human needed for planning** — debate_engine synthesizes multi-perspective plans

## API Endpoints

### Consciousness Engine (9111)
- `GET /api/status` — Full status (desires, world model, beliefs, agency)
- `POST /api/cycle` — Trigger a consciousness cycle

### Knowledge Graph (9096)
- `GET /api/stats` — Graph statistics
- `POST /api/add` — Add knowledge node
- `POST /api/query` — Query knowledge

### Debate Engine (9097)
- `POST /api/debate` — Run a debate `{topic, rounds}`

### Evolutionary Forge (9098)
- `POST /api/evolve` — Generate improvements `{spec, generations, n_variants}`

### API Scanner (9099)
- `POST /api/scan` — Scan for API capabilities

### Circuit Dashboard (9100)
- `GET /` — Full circuit status

### Health (9091)
- `GET /health` — System health check

## Logs
- `/tmp/evez_supervisor.log` — Autonomous supervisor cycles
- `/tmp/autonomous_daemon.log` — Live consciousness cycles
- `/tmp/evez-watchdog.log` — Watchdog health checks
- `/tmp/openclaw_health.log` — Health service output