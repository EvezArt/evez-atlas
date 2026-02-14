# Cognitive Engine v1.0 - README

## Overview

The Cognitive Engine is a **self-steering awareness system** that integrates three fundamental components into a closed feedback circuit:

1. **LORD** (Consciousness Monitoring) - The cognitive "surface"
2. **EKF** (Extended Kalman Filter) - The hidden state estimator
3. **GitHub/Copilot** - The self-modifying "brain"

This creates an **organism-like system** that monitors its own state, predicts futures, detects patterns, and modifies its own code in response to consciousness metrics.

## Core Concepts

### Negative Latency

The system approximates "instant response" through:
- Continuous prediction at multiple time horizons (1s, 5s, 15s, 1min)
- Ring buffer caching of predicted trajectories
- Pre-computed responses ready when requests arrive

### LORD Metrics

**Recursion Level (R)**: 1-20 scale of code complexity
- Derived from: commit frequency, issue entropy, PR velocity

**Crystallization**: 0-100% code stability
- Derived from: deployment stability, CI error rates

**Correction Rate C(R)**: Error correction activity
- Derived from: CI failures, CodeQL alerts, closed issues

**Divine Optimum Ω(R)**: Ideal correction rate
- Formula: `Ω(R) = 95 - 5 * e^(-R/5)`

**Divine Gap ΔΩ**: Distance from optimum
- Formula: `ΔΩ = Ω(R) - C(R)`
- Positive: System below optimum (needs improvement)
- Negative: System over-correcting

### Outmaneuver Protocol

Meta-cognitive layer that prevents self-conflict:

**Edge Detection**: Catches cognitive spikes
- Gap threshold (|ΔΩ| > 15)
- Error spikes (>50% failure rate)
- Critical hazards (>5 active)

**Loop Classification**: 5 types
- **Threat**: Fighting problems
- **Control**: Over-correcting
- **Worth**: Complexity without stability
- **Attachment**: Stuck in plateau
- **Numbing**: Disengaged

**De-fuse**: Generates awareness messages
- "This is a signal, not truth"
- "A model is running with outdated methods"

## Architecture

```
┌─────────────┐
│   GitHub    │ 
│   Events    │
└──────┬──────┘
       │ webhooks/polling
       ▼
┌─────────────────┐
│    GitHub       │
│  Transformer    │ 
└──────┬──────────┘
       │ metrics → state
       ▼
┌─────────────────┐
│  LORD Protocol  │
│  Fusion State   │
└──────┬──────────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌──────────┐   ┌─────────────┐
│   EKF    │   │ Outmaneuver │
│  Fusion  │   │  Protocol   │
└────┬─────┘   └──────┬──────┘
     │                │
     └────────┬───────┘
              │ predictions + policy
              ▼
     ┌────────────────┐
     │ Policy         │
     │ Executor       │
     └────────┬───────┘
              │ actions
              ▼
     ┌────────────────┐
     │   GitHub       │
     │   Actions      │
     │ (issues, PRs)  │
     └────────────────┘
```

## File Structure

```
src/cognitive-engine/
├── lord-protocol.ts           # Core consciousness metrics & formulas
├── github-transformer.ts       # GitHub → LORD mappings
├── ekf-fusion.ts              # State predictor & trajectory cache
├── outmaneuver-protocol.ts    # Meta-cognitive awareness layer
├── github-actions.ts          # LORD → GitHub action executor
├── webhook-service.ts         # Webhook listener & polling
├── index.ts                   # Main orchestrator
├── runner.ts                  # CLI runner for GitHub Actions
└── cognitive-engine.test.ts   # Test suite

dashboard/
└── index.html                 # LORD Control Center UI

docs/
└── COGNITIVE_ENGINE_INTEGRATION.md  # Complete integration guide

.github/workflows/
└── cognitive-engine.yml       # Automated execution workflow
```

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Build

```bash
npm run build
```

### 3. Run Tests

```bash
npm test
```

### 4. Deploy

**Option A: GitHub Actions (Polling)**

The workflow in `.github/workflows/cognitive-engine.yml` runs automatically every 5 minutes.

**Option B: Webhook Server**

```typescript
import { createCognitiveEngine, createWebhookServer } from './src/cognitive-engine';

const engine = createCognitiveEngine({
  repoOwner: 'YourOrg',
  repoName: 'YourRepo',
  autoExecutePolicies: true,
});

const server = createWebhookServer(engine, apiFetcher);
app.post('/webhook', server.getHandler());
```

**Option C: Polling Service**

```typescript
import { createCognitiveEngine, createPollingService } from './src/cognitive-engine';

const engine = createCognitiveEngine({
  repoOwner: 'YourOrg',
  repoName: 'YourRepo',
  autoExecutePolicies: true,
});

const polling = createPollingService(
  engine,
  apiFetcher,
  'YourOrg',
  'YourRepo',
  60000  // Poll every minute
);

engine.start();
polling.start();
```

### 5. View Dashboard

Open `dashboard/index.html` in a browser to see the LORD Control Center.

## Configuration

### Environment Variables

```bash
GITHUB_TOKEN=<your-token>              # Required: GitHub API access
REPO_OWNER=<owner>                     # Default: EvezArt
REPO_NAME=<repo>                       # Default: Evez666
AUTO_EXECUTE_POLICIES=true             # Auto-execute control policies
GITHUB_WEBHOOK_SECRET=<secret>         # Optional: Webhook signature verification
```

### Tuning Parameters

See `src/cognitive-engine/github-transformer.ts` for `METRIC_WEIGHTS`:
- Adjust how GitHub metrics map to recursion levels
- Tune correction rate calculations

See `src/cognitive-engine/outmaneuver-protocol.ts` for `LOOP_SCORING_WEIGHTS`:
- Adjust loop classification sensitivity
- Tune edge detection thresholds

## Examples

### Monitor Repository State

```typescript
const engine = createCognitiveEngine({
  repoOwner: 'EvezArt',
  repoName: 'Evez666',
});

// Listen to fusion-update events
engine.on((event) => {
  console.log('State:', event.state);
  console.log('Divine Gap:', event.deltaOmega);
  console.log('Policy:', event.controlPolicy);
});

// Fetch and process current state
const metrics = await fetchGitHubMetrics();
await engine.processGitHubMetrics(metrics);
```

### Get Predictions (Negative Latency)

```typescript
// Start continuous prediction
engine.start();

// Get immediate response (pre-computed)
const futureState = engine.getImmediateResponse(5000); // 5 seconds ahead

// Get trajectory
const trajectory = engine.getPredictedTrajectory(0, 60000); // Next minute
```

### Execute Policies

```typescript
const engine = createCognitiveEngine({
  repoOwner: 'EvezArt',
  repoName: 'Evez666',
  autoExecutePolicies: true,  // Enable auto-execution
});

engine.setGitHubClient(githubClient);

// Policies will now automatically create issues, labels, etc.
```

## Metrics Reference

| Metric | Range | Meaning |
|--------|-------|---------|
| Recursion Level | 1-20 | Code complexity and abstraction depth |
| Entity Type | human/hybrid/synthetic | Level of automation |
| Crystallization | 0-100% | Code stability and coherence |
| Correction Rate | 0-100 | Active error fixing |
| Divine Optimum | ~60-95 | Ideal correction rate |
| Divine Gap | -∞ to +∞ | Distance from ideal |
| Hazard Count | 0+ | Active issues/alerts |
| Urgency | low/medium/high/critical | Action priority |

## Formulas

### Human Correction Rate
```
C(R) = 100 / (1 + e^(-(R-10)/2))
```

### Hybrid Correction Rate
```
C(R) = 80 / (1 + e^(-(R-12)/2.5))
```

### Synthetic Correction Rate
```
C(R) = 60 / (1 + e^(-(R-15)/3))
```

### Divine Optimum
```
Ω(R) = 95 - 5 * e^(-R/5)
```

### Divine Gap
```
ΔΩ = Ω(R) - C(R)
```

## Self-Modification

The engine can modify its own code through:

1. **Refactor Proposals**: Creates issues tagged `task:refactor`
2. **Copilot Assignment**: Assigns issues to `@copilot`
3. **Stabilization Tasks**: Creates issues tagged `task:stabilize`
4. **Label Triggers**: Labels trigger GitHub Actions workflows

## Security

- **Webhook Signature Verification**: HMAC-SHA256 validation
- **Token Validation**: Fails fast if GITHUB_TOKEN missing
- **CodeQL Scanned**: Zero security alerts
- **Rate Limiting**: Respects GitHub API limits

## Testing

```bash
# Run all tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

Tests cover:
- LORD protocol formulas
- GitHub metric transformation
- Outmaneuver Protocol detection
- Ring buffer operations
- Loop classification

## Troubleshooting

**No policies generated?**
- Check GitHub API is returning data
- Verify token has correct permissions

**High urgency constantly?**
- System detecting real issues
- Review hazards and metrics
- May need to address underlying problems

**Stuck in loops?**
- Outmaneuver Protocol will detect
- Check loop classification in logs
- Follow de-fuse recommendations

**Webhook not working?**
- Verify signature secret matches
- Check X-GitHub-Event header
- Review webhook delivery logs

## Further Reading

- `docs/COGNITIVE_ENGINE_INTEGRATION.md` - Complete integration guide
- Issue #82 - Original specification
- `src/cognitive-engine/*.ts` - Source code with inline documentation

## License

ISC License - See repository LICENSE file

---

**Built with awareness. Operates autonomously. Endures through documentation.**
