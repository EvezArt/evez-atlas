# Compliant Aggregate Monitoring Blueprint

This document defines a **non-targeting**, **platform-compliant** monitoring approach for
understanding manipulation patterns at the **aggregate** level. It is explicitly designed
for **self-protection**, **platform reporting**, and **pattern analysis** — **not** for
naming individuals, harassment, or law enforcement action without chain-of-custody data.

## Guardrails (Non-Negotiable)

- **No individual targeting**: never label users as "bad actors" or identify them in outputs.
- **No harassment lists**: outputs are limited to **anonymized cluster IDs** and aggregates.
- **No ToS bypass**: **API-only** ingestion using your authorized credentials.
- **No attribution claims** beyond behavior-based, probabilistic patterns.
- **No "who pays whom"** claims from OSINT alone.
- **No law enforcement deliverables** without verified chain-of-custody.
- **If physical danger is suspected**, involve trained professionals and authorities.

## Allowed Data Sources

Use **only** the following:

- **Official platform APIs** (e.g., X API v2) within rate limits and account permissions.
- **User-provided CSV exports** derived from those official APIs.
- **Public, platform-provided datasets** that permit redistribution.
- **First-party logs** that you own and are authorized to analyze.

## Data Minimization & Privacy

- Hash identifiers (author IDs, post IDs) with **rotating salts per reporting period**.
- Store raw text **transiently**; persist **feature vectors and aggregates** only.
- Enforce **k-anonymity** thresholds (e.g., suppress metrics for groups < k=5).

## Pipeline Overview

1. **Ingest**
   - API/CSV -> normalized event records.
   - Minimal fields only (see schema below).
2. **Feature Extraction**
   - Aggregate metrics by time window and topic.
3. **Graph Construction**
   - Build timing/similarity/amplification graphs (anonymized nodes).
4. **Cluster Analysis**
   - Community detection on fused graphs (cluster IDs only).
5. **Risk Scoring**
   - Cluster-level scoring from behavioral signals (no identity signals).
6. **Reporting**
   - Privacy-preserving dashboards + exportable summaries.

## Minimal Event Schema (Suggested)

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

## Aggregate Metrics (Per Window)

- **Volume**: posts per window.
- **Velocity**: first derivative of volume.
- **Topic drift**: cosine distance between topic distributions.
- **Domain concentration**: Gini or top-k share for external domains.
- **Template similarity**: near-duplicate rate (MinHash/TF-IDF).

## Graphs & Clustering (Anonymized)

### Timing Graph
Edges connect anonymized authors that post within Δt on the same query/topic.

### Similarity Graph
Edges connect posts with high textual similarity (template reuse).

### Amplification Graph
Edges connect authors repeatedly boosting the same domains or sources.

### Community Detection
Use Leiden or label propagation on the fused graph. Outputs:

- `cluster_id`
- `size`
- `density`
- `persistence`
- `top_domains` (aggregated)

## Risk Scoring (Cluster-Level Only)

Behavioral risk score derived from **aggregate** signals:

```
Risk = f(coordination, disruption_proxy, inauthenticity, persistence, centralization)
```

- **Coordination**: synchrony + repeated co-targeting.
- **Disruption proxy**: bursty reply/quote ratios and negativity spikes.
- **Inauthenticity**: template reuse + domain concentration + burstiness.
- **Persistence**: recurrence across multiple windows.
- **Centralization**: hub dominance in fused graph.

> Outputs must **never** list or infer individual identities.

## Anomaly Detection

- **Velocity spikes**: windows exceeding Nσ from rolling baseline.
- **Domain spikes**: sudden dominance by a single domain.
- **Template spikes**: sharp jump in near-duplicate rates.
- **Recurrence**: same cluster reappears within 24–72 hours.

## Reporting Outputs (Safe by Design)

- **Dashboards**: trend charts, cluster summaries, anomaly alerts.
- **Exports**: CSV/JSON summaries, GEXF graphs with anonymized node IDs.
- **Redactions**: suppress any cluster with size < k.

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

## Operational Checklist

- [ ] Confirm API access scope and rate limits.
- [ ] Enable identifier hashing with rotating salts.
- [ ] Configure k-anonymity threshold (>= 5).
- [ ] Define rolling baseline windows.
- [ ] Validate that all exports exclude raw identifiers.

## Notes on Intent & Attribution

- Behavioral patterns can **suggest** likely objectives but **cannot** prove intent.
- Attribution is **probabilistic**; avoid deterministic labels.
- Use cautious language in all reports.

## Emergency Escalation

If credible physical danger is suspected, **stop analysis** and involve trained
professionals. The system is **not** a substitute for emergency response.
