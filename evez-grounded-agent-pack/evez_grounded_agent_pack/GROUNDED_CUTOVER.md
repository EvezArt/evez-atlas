
# EVEZ Grounded Cutover Checklist

## Hard rule
No mock balances. No fake revenue. No simulated cycle results presented as runtime truth.

## 1. Canonical surfaces
- Keep the longscale app as the canonical operator surface for backend-owned state.
- Keep the phone-first mobile surface as the operator entry surface.
- Use one deploy rail per surface. Kill duplicate deploy projects that emit contradictory health.

## 2. Endpoint wiring
Wire these first:
- `/api/agent-run` -> real n8n webhook
- `/api/chat` -> real provider proxy
- `/api/opportunities` -> live opportunities source
- `/api/wallet/treasury` + `/api/wallet/balances` + `/api/settlements` -> treasury provider + settlement source

## 3. Persistence
Move these off in-memory state:
- mission bus
- ledger entries
- workflow telemetry

Recommended backing:
- Redis / Bull for queue
- Postgres for ledger
- InfluxDB + Grafana for telemetry

## 4. Declared-only agent policy
The following roles remain declared but disabled until upstreams are real:
- scanner
- predictor
- generator
- shipper
- worldsim

Do not expose them in UI as operational if their upstreams are absent.

## 5. First safe expansion after cutover
- persistent bus storage
- signed ledger proofs
- workflow rerun controls
- command palette bound to real endpoints
- spawner-driven child MCP services for non-critical tooling
