# Quantum Threat Detection Mapping Spec (Aggregate, Compliant)

This spec defines a **non-targeting**, **platform-compliant** mapping approach for
aggregate threat detection using **quantum-inspired** techniques. It is scoped to
behavioral patterns and anonymized clusters — **never** individual identification
or harassment.

## Guardrails (Non-Negotiable)

- **No individual targeting** or “bad actor” labeling.
- **No harassment lists**; outputs are **cluster IDs only**.
- **API-only ingestion** under your authorized credentials.
- **Probabilistic attribution only**; no claims of “true intent.”
- **No OSINT-only financial attribution** (“who pays whom”).
- **If physical danger is suspected**, defer to trained professionals.

## System Goals

1. Identify **aggregate coordination patterns** and abnormal activity.
2. Provide **cluster-level risk scores** with clear, auditable signals.
3. Enable **privacy-preserving summaries** for reporting and internal review.

## Inputs (Allowed Sources)

- Official platform APIs (e.g., X API v2) within rate limits.
- User-provided CSV exports from those APIs.
- Public, platform-provided datasets with redistribution permission.
- First-party logs you are authorized to analyze.

## Minimal Event Schema

```json
{
  "post_id_hash": "sha256",
  "author_id_hash": "sha256",
  "timestamp": "ISO-8601",
  "text": "ephemeral_processing_only",
  "language": "en",
  "reply_to_post_id_hash": "sha256",
  "is_reply": true,
  "is_quote": false,
  "is_repost": false,
  "public_metrics": {
    "like_count": 0,
    "reply_count": 0,
    "repost_count": 0,
    "quote_count": 0
  },
  "domains": ["example.com"]
}
```

## Feature Pipeline (Aggregate)

### Windowing
- Sliding windows: **15m / 1h / 24h** (configurable).
- Baselines: rolling 7–30 day baselines per topic.

### Core Features
- **Volume**: posts per window, reply/quote ratios.
- **Velocity**: first derivative of volume.
- **Topic drift**: cosine distance between topic distributions.
- **Template similarity**: near-duplicate rate (MinHash/TF-IDF).
- **Domain concentration**: top-k share / Gini coefficient.
- **Burstiness**: inter-arrival variance vs. baseline.

## Quantum-Inspired Mapping Layer

> The “quantum” layer is **classical simulation** of quantum feature maps and
> kernels. It provides non-linear similarity scoring without claims of true
> quantum advantage.

### Quantum Feature Map (Simulated)
- Map each **aggregate feature vector** into a high-dimensional state.
- Use a rotation-based feature map (e.g., ZZFeatureMap simulation).

### Kernel Similarity
- Compute kernel values **K(x, y)** between time-window feature vectors.
- Use kernel similarities to:
  - detect **recurring coordination signatures**,
  - cluster windows with similar activity profiles,
  - score anomaly distances from baseline.

### Output
- A **kernel similarity graph** between aggregate windows or cluster centroids.
- No node represents an individual; nodes represent **time windows** or **clusters**.

## Graphs & Clustering (Anonymized)

### Timing Graph
- Edges connect anonymized authors co-posting within Δt.

### Similarity Graph
- Edges connect windows or clusters with high text/template similarity.

### Amplification Graph
- Edges connect clusters that repeatedly boost the same domains.

### Fused Graph
- Merge graphs with weighted edges and run community detection (Leiden or LPA).
- Output **cluster IDs only**.

## Risk Scoring (Cluster-Level Only)

```
Risk = f(coordination, disruption_proxy, inauthenticity, persistence, centralization)
```

- **Coordination**: synchrony + repeated co-targeting.
- **Disruption proxy**: reply ratio spikes + negativity bursts.
- **Inauthenticity**: template reuse + domain concentration + burstiness.
- **Persistence**: recurrence across windows.
- **Centralization**: hub dominance within cluster.

## Anomaly Detection

- **Velocity spikes** beyond Nσ baseline.
- **Template spikes** with near-duplicate surges.
- **Domain spikes**: sudden single-domain dominance.
- **Recurrence**: same cluster across 24–72h.

## Privacy-Preserving Outputs

- Cluster summaries with **anonymized IDs** only.
- Suppress clusters with size < k (k-anonymity).
- Export formats: CSV/JSON/GEXF with anonymized IDs.

## Example Cluster Summary

```json
{
  "cluster_id": "c-8b3f2",
  "window": "2024-01-01T00:00:00Z/2024-01-01T01:00:00Z",
  "size": 42,
  "density": 0.12,
  "persistence": 3,
  "risk_score": 0.68,
  "top_domains": ["news.example", "blog.example"],
  "alerts": ["velocity_spike", "template_spike"]
}
```

## Evaluation & Sequencing

- **Sequencing**: ingest → aggregate features → quantum kernel → cluster → score → report.
- **Evaluation**: validate alert precision against known incidents or test datasets.
- **Rollback**: disable clustering or kernel features if false positives exceed threshold.

## Notes on Interpretation

- This system **does not infer individual intent**.
- All outputs are **aggregate**, **anonymized**, and **probabilistic**.
- Use cautious, non-accusatory language in all reports.
