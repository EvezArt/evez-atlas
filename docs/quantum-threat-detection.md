# Quantum Threat Detection Mapping Spec (Authorized Use)

This spec outlines a conceptual, **authorized-use** mapping framework for detecting
aggregate anomalies in quantum-adjacent infrastructure (e.g., lab simulations,
research clusters, or controlled testbeds). It is **not** an exploitation guide
and must be applied only within explicitly approved scopes.

## Objectives

- Detect **aggregate** deviations in quantum pipeline telemetry without
  identifying or targeting individuals.
- Provide a repeatable mapping from **signals** to **risk tiers** with clear
  provenance and auditability.
- Ensure privacy-preserving analysis and compliance with local policies.
- Maintain a **run/validate loop** so the system “runs when it runs” and
  escalates safely when it does not.

## Scope & Guardrails

- **Authorized environments only** (lab, test range, or sanctioned assessment).
- **No adversarial instructions** or bypasses.
- **No individual attribution**; report at cluster or system level.
- **Minimize data retention** with explicit retention windows.

## System Map (Conceptual)

**Domains**

1. **Control Plane**: schedulers, orchestration metadata, access controls.
2. **Data Plane**: job execution telemetry, error logs, performance counters.
3. **Quantum Pipeline**: job manifests, calibration metadata, circuit metrics.
4. **Network Plane**: aggregate ingress/egress, timing skew, queue saturation.

**Primary Assets**

- Job manifests and execution timelines.
- Calibration and hardware state transitions.
- Aggregate network timing and queue stats.
- Integrity signals (signatures, checksums).

## Data Inputs (Aggregate Only)

Collect minimal features necessary for trend detection:

- **Job telemetry**: queue depth, execution duration, retry rates.
- **Calibration drift**: frequency deltas, error rates, variance bands.
- **Resource usage**: aggregate CPU/GPU/QPU utilization bands.
- **Network signals**: mean latency, jitter distribution, saturation windows.
- **Integrity checks**: signature pass/fail counts per window.

## Feature Windows & Baselines

- **Windows**: 5m / 30m / 24h (configurable).
- **Baselines**: rolling mean/variance, seasonal decomposition per window.
- **Normalization**: z-score per signal to compare across domains.

## Quantum Navigation (Probability Manifold Projection)

Use probabilistic projection to align signals across domains without attempting
to infer individual behavior:

- **State vector**: windowed, normalized signal bundle.
- **Projection**: map each state into a low-dimensional manifold (e.g., PCA or
  UMAP) to capture drift patterns.
- **Sequencing**: measure sequence divergence across consecutive windows to
  detect persistent shifts.

## Mapping: Signals → Risk Tiers

**Tier 0 — Baseline**

- Within expected variance bands.

**Tier 1 — Deviation**

- Single-domain anomaly (e.g., calibration drift spike) with low persistence.

**Tier 2 — Correlated**

- Multi-domain anomaly (e.g., calibration drift + queue saturation).

**Tier 3 — Persistent**

- Correlated anomalies across multiple windows with increasing severity.

**Tier 4 — Integrity Risk**

- Integrity check failures combined with persistent cross-domain anomalies.

## Detection Heuristics (Non-Exhaustive)

- **Drift bursts**: calibration variance > Nσ within a short window.
- **Latency spikes**: jitter distribution tail growth sustained for >2 windows.
- **Retry cascades**: elevated job retries aligned with control plane errors.
- **Signature failures**: integrity failure rate above a defined threshold.

## Reporting Format

**Cluster-Level Summary**

- `cluster_id` (anonymized, rotated per reporting period)
- `window` (time interval)
- `signals_triggered` (list of anomaly classes)
- `risk_tier` (0-4)
- `confidence` (low/medium/high)
- `notes` (human-readable, non-attributional)

## Run/Validate Loop

- **Run**: execute detectors on every window and log outcomes.
- **Validate**: compare anomalies to the baseline and recent history.
- **Uprun**: if validation fails (noisy or unstable), tighten thresholds or
  reduce scope before running again.

## Evidence & Auditability

- Maintain a short audit log with **signal hashes** and **timestamps**.
- Store only aggregate metrics and anonymized identifiers.
- Document model changes and thresholds in change logs.

## Escalation Guidance

- Tier 3–4 events require **human review** and **scope confirmation**.
- If physical safety is implicated, follow approved escalation protocols.

## Example Pseudocode (High-Level)

```
for window in windows:
    scores = normalize(signals[window])
    anomalies = detect(scores, thresholds)
    tier = map_to_risk_tier(anomalies)
    report(cluster_id, window, anomalies, tier)
```

## Compliance Checklist

- [ ] Scope and authorization recorded
- [ ] Aggregate-only data collection
- [ ] No individual identification or targeting
- [ ] Retention limits defined
- [ ] Audit logs enabled
