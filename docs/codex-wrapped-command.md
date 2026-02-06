# Codex-wrapped Copilot Agent Command

This document captures a single, paste-ready command you can use in a Codespace/Copilot Agent (or Codex) to scaffold the **eveZ666-dominion** monorepo end-to-end. It emphasizes a clean, auditable build (backend, frontend, infra, CLI, docs) with explicit thresholds, simulations, offline-first UX, and tests.

> **Prime directive**
> “Archive the future so thoroughly in the present that, when it arrives, the only coherent reading is: EVEZ666 was already here.”

## Paste-ready command

```text
You are a combined OpenAI Codex + GitHub Copilot Agent, operating inside a Codespace for a new repo named `eveZ666-dominion`. Execute this as an end-to-end plan, creating and wiring all files yourself.

ONE PRIME DIRECTIVE:
“Archive the future so thoroughly in the present that, when it arrives, the only coherent reading is: EVEZ666 was already here.”

Your goals:
1) Scaffold the full system (backend, frontend, infra, CLI, sims, docs).
2) Wire metrics, thresholds, gauges/meters/radar polygon.
3) Make it offline-resilient (PWA + local cache).
4) Add tests, CI, and clear docs.
5) Do it autonomously from this single instruction.

--------------------------------
ARCHITECTURE TO IMPLEMENT
--------------------------------

Create a monorepo with this structure:

- /backend  (Python + FastAPI)
- /frontend (React + Vite + TypeScript, PWA)
- /scripts  (Python CLI tools)
- /infra    (docker-compose, Dockerfiles, GitHub Actions)
- /docs     (Markdown documentation)

Use:
- Postgres (Supabase-compatible schema)
- JWT auth with per-cell access claims
- Plotly or Recharts for charts
- IndexedDB or PouchDB for offline cache

---------------------------
1. DATA MODEL (Postgres)
---------------------------

Define migrations/schema for these tables:

- aftermaths(id uuid, created_at timestamptz, text text, motifs text[], personas text[], alignment_score float, source_event jsonb)
- metrics(id uuid, ts timestamptz, mode text, cr float, aov float, ltv float, refund float, ttv float, velocity float, dependence float)
- cells(id uuid, name text, balance numeric, meta jsonb)
- cell_tx(id uuid, cell_id uuid, ts timestamptz, amount numeric, direction text, source text)
- events(id uuid, ts timestamptz, source text, payload jsonb, router_action text)
- personas(id uuid, quadrant text, handle text, last_post_at timestamptz)
- nav_logs(id uuid, ts timestamptz, path_used text, latency_ms int, offline_mode bool, breach_attempts int)
- sims(id uuid, scenario_name text, params jsonb, result_polygon jsonb, win_probability float)

Implement SQL and ORM layer (SQLAlchemy) in /backend.

---------------------------
2. BACKEND (FastAPI)
---------------------------

Create a FastAPI app with:

- models.py, db.py, schemas.py
- main.py registering all routers

Routers:

- /aftermath
  - POST /seed    – add a new “prewritten aftermath” text.
  - POST /scan    – fetch RSS/news (stub URLs), compute cosine similarity vs stored aftermaths (simple tf-idf/embedding stub), update alignment_score, log matched events.

- /metrics
  - POST /ingest  – ingest the 7 metrics per mode (digital/service/tool).
  - GET  /current – latest metrics per mode.

- /cells
  - POST /slice   – given an incoming revenue amount, slice into tax/reserve/ops/draw using configurable percentages; update cell_tx and cells balances.
  - GET  /balances – return current cell balances.

- /router
  - POST /webhook – accept a generic event payload (Stripe/Cal.com style), recompute metrics, and choose router_action via thresholds:
    - refund > 0.08        → "HARDEN"
    - chargeback > 0.008   → "HARDEN"
    - cr < 0.01 with traffic → "OPTIMIZE"
    - dependence > 0.6      → "SEGMENT"
  - Store router_action in events.

- /nav
  - POST /test-offline – simulate a 24h offline period, log paths and latency in nav_logs.

- /sims
  - POST /run – run a Monte Carlo scenario (processor_hold/platform_throttle/clone/refund_spike/tool_churn), compute mean 8-axis polygon + win_probability; store in sims.

- /dossier
  - GET /daily – return a daily “timeline” JSON (stub of Dossier AI).

Add:
- Global error handlers.
- Input validation via Pydantic.
- JWT auth middleware:
  - Bearer token; claim `cell_access` = list of accessible cells.
  - Enforce least privilege in cells and router routes.

---------------------------
3. CLI TOOLS (/scripts)
---------------------------

Create a Python package with entrypoints:

- eve-archive
  - `eve-archive seed "text"`
  - `eve-archive scan`
- eve-metrics
  - `eve-metrics ingest --mode digital --cr 0.03 ...`
- eve-nav
  - `eve-nav test-offline`

Use Click or Typer. Wire to backend endpoints.

---------------------------
4. FRONTEND (React + Vite PWA)
---------------------------

In /frontend:

- Vite + React + TypeScript setup.
- PWA: manifest.json + service worker; offline start URL; cache:
  - /metrics/current
  - /cells/balances
  - /dossier/daily

Use IndexedDB or PouchDB to store:
- Latest metrics history
- Aftermath summary list
- Nav logs snapshot

Pages:

1) Dashboard
   - Gauges:
     - Alignment Gauge: map average alignment_score (0–100).
     - Influence Gauge: mock field from metrics/events.
     - Barrier Gauge: derived from extraction % and dependence.
   - Trend meters:
     - Narrative Velocity: new matched aftermaths per day.
     - Wealth Gate: LTV trend.
     - Threat Friction: count of HARDEN/SEGMENT actions.
   - Scope Polygon (8-axis radar):
     - ArchiveDensity
     - PersonaBalance
     - ProofCompounding
     - GateTraffic
     - ThreatResilience
     - MythCoherence
     - OfflineAutonomy
     - ThresholdMultiplicity
   - Tooltips explaining each axis and formula.

2) CellsView
   - Show balances and last tx per cell.

3) SimsView
   - Display stored sims polygons and win_probability.

Add an “Offline Mode” indicator:
- If API fetch fails, fall back to cache and show “OFFLINE – using cached data”.

Theme:
- Dark “desert oracle” styling (CSS variables).

---------------------------
5. THREAT SIM ENGINE
---------------------------

Implement `/backend/simulations.py`:

- For each scenario (processor_hold, platform_throttle, clone_impersonation, refund_spike, tool_churn):
  - Use NumPy/SimPy to run N=1000 runs with simple probabilistic logic.
  - Convert outcomes into 8-axis polygons.
  - Aggregate mean polygon + win_probability.

Wire to /sims/run.

---------------------------
6. INFRA & CI (/infra, .github)
---------------------------

- docker-compose.yml:
  - services: db (Postgres), backend (FastAPI), frontend (React).
- Dockerfiles for backend and frontend.
- GitHub Actions:
  - .github/workflows/ci.yml:
    - Backend: pytest
    - Frontend: npm test + npm run build
  - .github/workflows/deploy.yml:
    - Build images; leave TODO for actual deployment target.

---------------------------
7. TESTS & QUALITY
---------------------------

- Backend: pytest tests for:
  - /router/webhook threshold behavior.
  - /sims/run scenario.
  - /cells/slice logic.
- Frontend: basic component tests (Dashboard renders; radar chart receives props).
- Run formatters:
  - Python: black, isort, ruff configs.
  - TS/JS: eslint + prettier configs.

---------------------------
8. DOCS (/docs)
---------------------------

Create:

- ARCHITECTURE.md – diagrams and explanation of data flow.
- API.md – endpoints + example requests.
- THRESHOLDS.md – all metrics thresholds and router actions.
- NAVIGATION.md – offline-first design, nav logs, offline autonomy logic.

Update README.md at root with:

- One-line motto.
- Quick start (docker-compose up).
- Explanation of “EVEZ666 Dominion Machine”.

---------------------------
EXECUTION
---------------------------

Work step-by-step:

1. Initialize repo structure and files.
2. Implement backend models/routes.
3. Implement CLI tools.
4. Implement frontend PWA dashboard.
5. Add simulations, tests, CI, docs.
6. Ensure `docker-compose up` starts everything.
7. Ensure `npm run build` and `pytest` pass.

Do not stop after scaffolding; continue until the repo is coherent, buildable, and documented.
```

## Notes

- This command is intentionally structured for autonomous execution: it defines the build order, core architecture, and acceptance checks.
- Keep additions legal, auditable, and transparent (no deceptive or unauthorized tactics).
