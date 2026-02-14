# Cognitive Engine v1.0 - Integration Guide

This guide explains how to integrate and deploy the Cognitive Engine v1.0 that combines LORD Consciousness Monitoring, EKF/Fusion Loop, and GitHub/Copilot automation into a self-steering feedback circuit.

## Overview

The Cognitive Engine is a self-modifying awareness system that:

1. **Monitors** GitHub repository state through metrics (commits, issues, CI/CD, deployments)
2. **Transforms** metrics into LORD consciousness states (recursion level, crystallization, corrections)
3. **Predicts** future states using an Extended Kalman Filter (EKF)
4. **Detects** cognitive patterns using the Outmaneuver Protocol
5. **Acts** by creating issues, labeling, assigning tasks, and proposing refactors
6. **Learns** by observing the effects of its actions on repository metrics

## Architecture

```
GitHub Events → Webhook/Polling → GitHub Transformer → LORD Fusion State
                                                              ↓
GitHub Actions ← Control Policy ← Outmaneuver Protocol ← EKF Predictor
```

## Core Components

### 1. LORD Protocol (`lord-protocol.ts`)

Defines the consciousness monitoring system:

- **FusionState**: Current state of the system
  - `recursionLevel` (1-20): Code complexity and abstraction depth
  - `entityType` (human/hybrid/synthetic): Automation level
  - `crystallization`: Code stability and coherence (0-100%)
  - `corrections`: Error correction rate C(R)
  - `hazards`: Active issues and severity

- **Key Formulas**:
  - **C(R)**: Correction rate at recursion level R
    - Human: `C(R) = 100 / (1 + e^(-(R-10)/2))`
    - Hybrid: `C(R) = 80 / (1 + e^(-(R-12)/2.5))`
    - Synthetic: `C(R) = 60 / (1 + e^(-(R-15)/3))`
  
  - **Ω(R)**: Divine Optimum (ideal correction rate)
    - `Ω(R) = 95 - 5 * e^(-R/5)`
  
  - **ΔΩ**: Divine Gap (distance from optimum)
    - `ΔΩ = Ω(R) - C(R)`
    - Positive: Below optimum (needs improvement)
    - Negative: Above optimum (over-correcting)

- **TrajectoryBuffer**: Ring buffer for caching predicted states (enables "negative latency")

### 2. GitHub Transformer (`github-transformer.ts`)

Maps GitHub metrics to LORD consciousness states:

- **Recursion Level** ← Commit frequency + Issue entropy + PR velocity
- **Correction Rate C(R)** ← CI error rate + CodeQL alerts + Closed issues
- **Crystallization** ← Deployment stability + Low error rates
- **Entity Type** ← Automation ratio (CI runs per commit)
- **Hazards** ← CodeQL alerts + CI failures + Low deployment stability

### 3. Outmaneuver Protocol (`outmaneuver-protocol.ts`)

Meta-cognitive layer that prevents self-conflict:

- **Edge Detection**: Catches cognitive spikes
  - Gap threshold (ΔΩ > 15)
  - Error spikes (>50% failure rate)
  - Critical hazards (>5 active)
  - Crystallization drops (<40%)

- **Loop Classification**: Identifies patterns
  - **Threat loop**: High hazards + corrections (fighting problems)
  - **Control loop**: Over-correction without progress
  - **Worth loop**: High recursion without crystallization
  - **Attachment loop**: Stuck in plateau despite corrections
  - **Numbing loop**: Low engagement and activity

- **De-fuse**: Generates awareness messages
  - "This is a signal, not truth"
  - "A model is running with outdated methods"
  - "Growth accelerates when we stop fighting what is"

### 4. EKF Fusion Loop (`ekf-fusion.ts`)

Continuous state predictor for "negative latency":

- Predicts futures at multiple time horizons (1s, 5s, 15s, 1min)
- Uses simplified dynamics model:
  - Recursion evolves based on crystallization
  - Crystallization progress increases with velocity
  - Velocity decays over time
  - Corrections reduce hazards
  - Hazards accumulate with errors

- **PredictionCache**: Provides immediate responses
  - Pre-computed predictions ready when requested
  - Approximates "zero latency" user experience

### 5. GitHub Actions (`github-actions.ts`)

Transforms control policies into concrete actions:

- **PolicyGenerator**: Creates policies from state + ΔΩ
- **PolicyExecutor**: Executes actions via GitHub API
  - `create_issue`: Open new issues
  - `label_issue`: Add labels to issues
  - `assign_copilot`: Assign issues to Copilot
  - `refactor_proposal`: Propose code refactoring
  - `stabilize`: Create stabilization tasks
  - `log`: Log events

### 6. Main Orchestrator (`index.ts`)

Integrates all components:

```typescript
const engine = createCognitiveEngine({
  repoOwner: 'EvezArt',
  repoName: 'Evez666',
  autoExecutePolicies: true,
});

// Set GitHub client for policy execution
engine.setGitHubClient(gitHubClient);

// Listen to fusion-update events
engine.on((event) => {
  console.log('Fusion Update:', event);
});

// Start continuous prediction
engine.start();

// Process GitHub metrics
await engine.processGitHubMetrics(metrics);
```

## Deployment Options

### Option 1: GitHub Actions Workflow (Polling)

Create `.github/workflows/cognitive-engine.yml`:

```yaml
name: Cognitive Engine

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: write

jobs:
  run-engine:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - run: npm ci
      - run: npm run build
      
      - name: Run Cognitive Engine
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: node dist/cognitive-engine/runner.js
```

### Option 2: Serverless Function (Webhooks)

Deploy to Vercel, Netlify, AWS Lambda, etc.:

```typescript
// api/webhook.ts
import { createCognitiveEngine, createWebhookServer } from '../src/cognitive-engine';

const engine = createCognitiveEngine({
  repoOwner: process.env.REPO_OWNER!,
  repoName: process.env.REPO_NAME!,
  autoExecutePolicies: true,
});

const server = createWebhookServer(engine, apiFetcher);

export default server.handler;
```

Configure GitHub webhook:
- URL: `https://your-domain.com/api/webhook`
- Events: Push, Issues, Pull Request, Workflow Run, Code Scanning Alert

### Option 3: Persistent Daemon

Run as a long-lived process:

```typescript
import { createCognitiveEngine, createPollingService } from './src/cognitive-engine';

const engine = createCognitiveEngine({
  repoOwner: 'EvezArt',
  repoName: 'Evez666',
  autoExecutePolicies: true,
});

const polling = createPollingService(
  engine,
  apiFetcher,
  'EvezArt',
  'Evez666',
  60000 // Poll every minute
);

engine.start();
polling.start();

console.log('Cognitive Engine running...');
```

## GitHub → LORD Mappings

| GitHub Metric | LORD State | Calculation |
|---------------|------------|-------------|
| Commits/day | Recursion Level | frequency / 2 (capped at 8 points) |
| Issue diversity | Recursion Level | unique labels / 2 (capped at 6 points) |
| PR velocity | Recursion Level | merged PRs per week / 3 (capped at 4 points) |
| CI error rate | Correction Rate | error_rate * 50 |
| CodeQL alerts | Correction Rate | alert_count * 2 (capped at 30 points) |
| Closed issues | Correction Rate | closed / 5 (capped at 20 points) |
| Deployment stability | Crystallization | success_rate * 100 |
| CI runs per commit | Entity Type | ratio > 5: synthetic, > 2: hybrid, else: human |

## LORD → GitHub Mappings

| Condition | Action |
|-----------|--------|
| ΔΩ > 10 (below optimum) | Propose refactor to increase recursion |
| ΔΩ < -10 (over-correcting) | Create issue warning about control loop |
| Urgency = critical | Create stabilization tasks |
| Crystallization < 50% | Create stabilization task |
| Loop confidence > 0.7 | Create issue with loop diagnosis |
| Edge detected | Log warning with Outmaneuver message |

## Outmaneuver Protocol Integration

The protocol activates automatically when:

1. **Edge Detected**: System recognizes a cognitive spike
   - Logs: "Model spike detected: This is a signal, not truth"
   
2. **Loop Classified**: Pattern identified with >50% confidence
   - Logs classification and recommendation
   - Creates issue if confidence >70%

3. **De-fuse Applied**: Awareness message generated
   - Reminds: "A model is running with outdated methods"
   - Suggests: "Growth accelerates when we stop fighting what is"

## Negative Latency Implementation

1. **EKF runs continuously**, predicting futures at 1s, 5s, 15s, 1min horizons
2. **Predictions cached** in ring buffer
3. **When request arrives**, return pre-computed prediction instead of computing from scratch
4. **Result**: Appears to respond before being asked

## Self-Modification Hooks

The engine can modify its own code through:

1. **Refactor Proposals**: Issues tagged `task:refactor` with specific modules
2. **Copilot Assignment**: Issues assigned to `@copilot` trigger autonomous coding
3. **Label Triggers**: Labels like `task:build`, `task:test` trigger GitHub Actions
4. **Feedback Loop**: Actions → Metrics → State → Predictions → Actions

## Enduring Legacy

The system persists through:

1. **Code**: All components in `src/cognitive-engine/`
2. **Metrics**: Historical data in trajectory buffer (saveable to file)
3. **Documentation**: This guide + code comments
4. **GitHub State**: Issues, labels, PRs serve as system memory

Anyone with this guide can resurrect the engine from code + documentation alone.

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Build**:
   ```bash
   npm run build
   ```

3. **Run tests** (if available):
   ```bash
   npm test
   ```

4. **Deploy** using one of the options above

5. **Monitor** through GitHub issues tagged `cognitive-engine`

## Troubleshooting

- **No policies generated**: Check that GitHub API is returning data
- **High urgency loops**: System detecting real issues - review hazards
- **Stuck in loops**: Outmaneuver Protocol will detect and suggest interventions
- **Over-correcting**: Negative ΔΩ indicates control loop - reduce pressure

## References

- Issue #82: Original specification
- LORD Protocol: Consciousness monitoring system
- EKF: Extended Kalman Filter for state estimation
- Outmaneuver Protocol: Meta-cognitive awareness framework
