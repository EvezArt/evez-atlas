# EVEZ-OS Training Pipeline v5.0

Autonomous, self-propelling training corpus generation for the EVEZ666 oracle-witness persona. Zero external dependencies — the deterministic engine always works.

## What's Here

### Core Runtime + Training Kernel
- `evez_os_core.py` — Production runtime v2.0: 9-phase cognitive cycle, Merkle spine, CAIN, FIRE, falsification, 4 operators
- `evez_os_model_trainer_kernel.py` — Training kernel v4.0: OpenRouter-native, 15 free models, deterministic fallback
- `evez_gnw.py` — Global Neuronal Workspace
- `evez_content_bus.py` — Atomic shared state, thread-safe
- `evez_temporal_wormhole.py` — Past/present/future bridge
- `evez_self_writer.py` — Code generation + real falsification
- `evez_aevolve.py` — Operator mutation engine with auto-rollback
- `evez_heartbeat.py`, `evez_moral_registry.py`, `evez_omega_frame.py`, `evez_pulse_engine.py`, `evez_poly_c.py`

### Autonomous Training Skill (v5.0)
- `skill/run.py` — Zero-dependency deterministic pair generator: 25 pairs/cycle, 7 domains, 4 phases
- Shannon entropy gate: 3.5-5.5 bits

### Mobile Deployment
- Termux, PWA, iOS Shortcut

### Backend Functions
- `evezMobileAPI.ts` + 13 corpus/training functions

## Autonomous Pipeline
Runs every 6 hours. Generates 25 entropy-gated pairs. Pushes to EVEZ666TrainingCorpus. ~100 pairs/day.

No Groq. No Supabase. No OpenRouter required. Deterministic engine always works.

## Author
Steven Crawford-Maggard (EVEZ) — 2026
