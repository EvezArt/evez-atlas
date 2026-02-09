# Threshold Navigation Mesh

**EVEZ666 Offline-Resilient, Zero-Trust Gated Architecture**

## Overview

The Threshold Navigation Mesh is a critical upgrade to the EVEZ666 system that ensures all resource flows (wealth/info/myth) remain operational when connectivity is latent, with ironclad gatekeeping at every access point.

## Architecture

The system consists of eight integrated components:

### 1. PWA Offline Cockpit

**Location:** `src/pwa/`

The Progressive Web App foundation provides offline-first operation:

- **manifest.json**: PWA manifest with desert glyphs theme (#1a1a2e / #e2b714 / #0f3460)
- **service-worker.js**: Workbox-based ServiceWorker with:
  - Asset caching (gauges, polygon viz, ledger views)
  - Stale-while-revalidate for API calls
  - POST request queuing for offline replay
  - Background sync for PouchDB ↔ remote sync
- **offline-store.ts**: IndexedDB/PouchDB wrapper with three stores:
  - `NavLogStore`: path_used, latency_ms, breach_attempts, timestamp
  - `ResourceCache`: cached revenue sims, RSS feed snapshots, draft posts
  - `GateState`: JWT tokens per cell, anomaly counters, lockdown flags

### 2. Threshold Gate Logic

**Location:** `src/gates/`

Zero-trust ingress control for all cell access:

#### Zero Trust Gate (`zero-trust.ts`)

- **JWT validation per cell**: archive, revenue, persona, router
- **Rate limiting**: 100 requests/minute per flow
- **Anomaly detection**: Flags >3x normal request rate
- **Auto-lockdown**: Isolates compromised cell, continues others

Key methods:
```typescript
validateGate(cell, token, context) → { allowed, reason }
detectAnomaly(flowMetrics) → { isAnomaly, severity, action }
```

#### Threshold Router (`threshold-router.ts`)

Multi-route navigation with failover:

- **Route definitions**: Primary → Secondary → Local-only
- **Path switching metrics**: Tracks switches per week
- **Failover logic**: Automatic degradation to local mode

Key methods:
```typescript
routeRequest(threshold, payload) → RouteResult
getNavVelocity() → NavVelocity
```

### 3. Latent Resource Flows

**Location:** `src/flows/`

Offline-capable resource handling for three thresholds:

| Threshold | Gate Mechanism | Latent Nav |
|-----------|----------------|------------|
| **Wealth (revenue)** | Cell slicing + failover processors | Local Stripe sim + cached payouts |
| **Info (archive)** | PouchDB + RSS proxy | Offline scan/match + opportunistic sync |
| **Myth (posts)** | Persona queue + SMS fallback | Local draft → burst on reconnect |

#### Wealth Flow (`wealth-flow.ts`)

Revenue cell with offline simulation:

- Local Stripe mock for revenue simulation when offline
- Cached payout calculations (1-hour TTL)
- Processor failover: Stripe → Local sim
- Cell slicing: Partition by digital/service/tool

#### Info Flow (`info-flow.ts`)

Archive cell with offline scan:

- PouchDB-backed document store
- RSS proxy cache (fetch + cache feeds)
- Offline search engine (local scan/match)
- Opportunistic sync when connectivity returns

#### Myth Flow (`myth-flow.ts`)

Persona/narrative cell:

- Post queue: draft locally → burst-publish on reconnect
- SMS fallback via webhook queue (EmailJS/Twilio stub)
- Persona rotation queue (schedule switches)
- Narrative seeding pipeline (aftermath content stubs)

#### Circuit Audit Bridge (`circuit-audit-bridge.ts`)

Connects profit circuit → audit system:

- Shared event format
- Event types: revenue, payout, gate, flow, anomaly
- Severity levels: info, warning, error, critical
- Conversion to audit log entries

### 4. Metrics & Gauges System

**Location:** `src/metrics/`

#### Gauges (`gauges.ts`)

Seven gauges on 0-100 scale:

1. **LatencyTolerance**: % operations surviving 24h offline (target: 100%)
2. **ThresholdLock**: % gate breach attempts blocked (target: 100%)
3. **ResourceFlow**: Ratio of cached vs live throughput (target: 50%)
4. **ArchiveDepth**: Document coverage (target: 80%)
5. **PersonaEntropy**: Diversity and rotation (target: 70%)
6. **ProofDensity**: Audit trail completeness (target: 90%)
7. **ThreatAwareness**: Anomaly detection effectiveness (target: 85%)

#### Meters (`meters.ts`)

Three trend meters:

1. **NavVelocity**: Path switches/week × success rate
2. **GateDensity**: Thresholds enforced across cells
3. **FlywheelMomentum**: Digital/service/tool revenue correlation

#### Scope Polygon (`scope-polygon.ts`)

8-axis visualization (0-10 each):

- Archive, Persona, Proof, Gate, Threat, Myth, NavLatency, ResourceLock
- Exports: ASCII art, JSON, SVG (desert glyphs theme)
- Metrics: area (coverage), balance (uniformity)

### 5. Navigation Mesh Database

**Location:** `src/db/nav-schema.sql`

PostgreSQL schema with four tables:

```sql
nav_logs       -- Path usage, latency, breaches
gate_state     -- Cell JWT, anomalies, lockdowns
resource_cache -- Offline cache with sync status
circuit_events -- Audit events from flows
```

Plus four views:
- `v_latency_tolerance`: Hourly offline capability %
- `v_gate_breaches`: Active anomalies and lockdowns
- `v_resource_sync_status`: Cache sync state
- `v_circuit_events_summary`: Event aggregation

### 6. CLI Commands

**Location:** `src/cli/nav-cli.ts`

Five commands:

```bash
# Test offline resilience
eve-nav test-offline [hours]

# Show gate status
eve-nav gate-status

# Force sync
eve-nav sync-force

# Check route health
eve-nav route-check <wealth|info|myth>

# Dashboard view
eve-nav dashboard
```

### 7. Threat Simulations

**Location:** `src/sims/latent-outage.ts`

Monte Carlo simulation for extended connectivity loss:

- **Scenarios**: 1h → 72h outage duration
- **Metrics**: Data loss, revenue impact, narrative gap
- **Output**: Survival score, weak points, cache size recommendations

Example output:
```
Average Survival Score: 87.3
Worst Case: 48h, 35% data loss, $1,200 revenue impact
Best Case: 2h, 2% data loss, $50 revenue impact
```

### 8. Integration Points

#### Profit Circuit → Audit System

The `CircuitAuditBridge` connects `run_profit_circuit.py` outputs to `audit_log_analyzer.py`:

1. Revenue events from wealth flow
2. Gate validation events
3. Anomaly detection events
4. Flow operation events

#### Metrics Router

All flows emit structured events consumed by the metrics system:

```typescript
// Flow emits event
bridge.emitCircuitEvent(bridge.createRevenueEvent(amount, processor));

// Metrics consume event
gauges.calculateLatencyTolerance(offlineOps, totalOps);
meters.calculateNavVelocity(pathSwitches, successRate);
polygon.calculatePolygon(allMetrics);
```

## Offline Operation

The system is designed to operate **entirely offline** for up to 72 hours:

### Data Persistence

- **IndexedDB**: Local browser storage (quota: ~50MB)
- **PouchDB**: Document database with CouchDB sync
- **ServiceWorker Cache**: Asset storage (~100MB)

### Offline Capabilities

1. **Revenue processing**: Local Stripe simulation
2. **Archive search**: Cached document index
3. **Post drafting**: Local queue with burst-publish
4. **Metrics tracking**: All calculations local
5. **Gate validation**: Cached JWT tokens

### Sync Strategy

- **Opportunistic**: Push/pull when connectivity returns
- **Conflict resolution**: Last-write-wins with metadata
- **Batch uploads**: Queued POST requests replayed in order

## Zero-Trust Security

Every request validates through the gate system:

### Validation Flow

```
Request → JWT Check → Rate Limit → Anomaly Detection → Cell Access
```

### Anomaly Actions

| Severity | Action | Description |
|----------|--------|-------------|
| 0-40 | Warn | Log anomaly, allow request |
| 41-75 | Throttle | Reduce rate limit 50% |
| 76-100 | Lockdown | Isolate cell, reject all |

### Cell Isolation

When a cell enters lockdown:

1. All requests to that cell are denied
2. Other cells continue operating normally
3. Metrics dashboard shows lockdown status
4. Manual release required via CLI

## Metrics Dashboard

The system health is visualized through:

### Gauges Panel

```
LatencyTolerance:  [████████████████████] 98%  ✓ OPTIMAL
ThresholdLock:     [███████████████████░] 96%  ✓ OPTIMAL
ResourceFlow:      [██████████░░░░░░░░░░] 48%  ✓ GOOD
```

### Meters Panel

```
NavVelocity:       8.5 switches/week  ↗ INCREASING
GateDensity:       100%                → STABLE
FlywheelMomentum:  92 correlation     ↗ INCREASING
```

### Scope Polygon

```
        Archive
         /   \
  NavLatency   Persona
       |         |
ResourceLock   Proof
       |         |
     Threat    Gate
         \   /
          Myth
          
Area: 78.3%  Balance: 85.1%
```

## Deployment

### Prerequisites

- Node.js 20.x
- PostgreSQL 14+
- Modern browser with ServiceWorker support

### Installation

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Initialize database
psql -f src/db/nav-schema.sql

# Run tests
npm test

# Start CLI
node dist/cli/nav-cli.js dashboard
```

### Environment Variables

```bash
# Optional: Database connection
DATABASE_URL=postgres://localhost/evez666

# Optional: Remote sync endpoint
SYNC_ENDPOINT=https://sync.evez666.com

# Optional: SMS webhook
SMS_WEBHOOK_URL=https://hooks.zapier.com/...
```

## Testing

Comprehensive test suites verify all functionality:

```bash
# Run all tests
npm test

# Specific test suites
npm test -- src/gates/gates.test.ts
npm test -- src/flows/flows.test.ts
npm test -- src/metrics/metrics.test.ts

# Coverage report
npm test -- --coverage
```

### Test Scenarios

- **Gates**: JWT validation, rate limiting, anomaly detection
- **Flows**: Offline operations, failover, queue processing
- **Metrics**: Gauge calculations, trend detection, polygon rendering
- **Integration**: End-to-end offline simulation

## Performance

Target metrics for optimal operation:

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| Latency Tolerance | 100% | >80% | <60% |
| Offline Duration | 72h | 48h | 24h |
| Data Loss | 0% | <5% | <20% |
| Revenue Capture | 100% | >70% | <50% |
| Narrative Gap | 0 posts | <3 posts | <10 posts |

## Troubleshooting

### Issue: High data loss

**Solution**: Increase IndexedDB cache size
```typescript
// In offline-store.ts
const CACHE_SIZE_MB = 100; // Increase from 50
```

### Issue: Gate false positives

**Solution**: Adjust anomaly threshold
```typescript
// In zero-trust.ts
private readonly ANOMALY_THRESHOLD = 5.0; // Increase from 3.0
```

### Issue: Poor sync performance

**Solution**: Enable batch uploads
```typescript
// In offline-store.ts
const BATCH_SIZE = 50; // Increase from 10
```

## Future Enhancements

1. **Conflict Resolution UI**: Manual conflict resolution interface
2. **Predictive Failover**: ML-based route health prediction
3. **Distributed Sync**: P2P sync between multiple clients
4. **Hardware Security**: WebAuthn integration for gate validation
5. **Edge Computing**: CloudFlare Workers for global sync

## References

- [PWA Best Practices](https://web.dev/progressive-web-apps/)
- [Zero Trust Architecture](https://www.nist.gov/publications/zero-trust-architecture)
- [IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [ServiceWorker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

---

**Status**: ✓ IMPLEMENTED  
**Version**: 1.0.0  
**Last Updated**: 2026-02-09
