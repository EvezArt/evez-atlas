# A012 Telemetry & Coincidence Data

This directory stores A012's running ledger.
All files are append-only JSONL.

## Files

- `predictions.jsonl` — PHASE1 precommit predictions (one per round, pre-tick)
- `prediction_scores.jsonl` — PHASE2 scoring receipts (post-tick actuals vs predicted)
- `coincidences.jsonl` — Coincidence scan results (per round)
- `lookahead_table.jsonl` — Rolling 10-round lookahead (updated each run)
