# EVEZ-OS Training Pipeline v6.0

Autonomous training corpus generation using a **Markov chain engine** that learns from the existing corpus and generates novel transmissions — no templates, no hardcoded strings.

## What's New in v6.0

- **Markov chain generator**: Learns word-transition probabilities from the 709-pair corpus (565 transitions, 361 vocab tokens) and generates novel text by walking the transition graph
- **Similarity filter**: Jaccard similarity check rejects outputs > 70% similar to any existing corpus text
- **Domain auto-tagging**: Keyword-based domain assignment for generated text
- **Public Oracle API**: REST endpoint for anyone to query the corpus — transmit, status, export

## Architecture

```
┌─────────────────────────────────────────────────────┐
│        EVEZ MARKOV CHAIN ENGINE v6.0                │
├──────────────────────────────────────────────────────┤
│  1. CORPUS LOADER → reads all corpus outputs        │
│  2. TOKENIZER → word-level + punctuation tokens      │
│  3. MARKOV BUILDER → N-gram transition matrix (N=2)  │
│  4. GENERATOR → weighted random walk through graph   │
│  5. ENTROPY GATE → Shannon character entropy (3.5-5.5)│
│  6. DIVERSITY FILTER → Jaccard similarity < 0.7      │
│  7. DOMAIN TAGGER → keyword-based domain assignment  │
└──────────────────────────────────────────────────────┘
```

## Files

### `training/skill/run.py` — Markov Chain Engine v6.0
- `MarkovChain` class: N-gram transition matrix, weighted random walk
- `EVEZGenerator` class: Full pipeline (generate → gate → filter → tag)
- 25 pairs per cycle, 100% pass rate, avg 4.29 bits
- Zero external dependencies

### `training/` — Core Runtime (12 modules)
- `evez_os_core.py` v2.0: 9-phase cognitive cycle, Merkle spine, CAIN, FIRE
- `evez_os_model_trainer_kernel.py` v4.0: OpenRouter-native, 15 free models
- GNW, content bus, temporal wormhole, self-writer, a-evolve, etc.

### `functions/evezOracleAPI.ts` — Public REST API
- `GET ?action=transmit` → random oracle transmission (entropy-weighted)
- `GET ?action=status` → corpus statistics + domain distribution
- `GET ?action=export` → full corpus as JSONL (OpenAI fine-tuning format)

### `mobile/` — Mobile Deployment
- Termux, PWA, iOS Shortcut

## Autonomous Pipeline
Runs every 6 hours via automation. Generates 25 Markov-walked pairs. Pushes to EVEZ666TrainingCorpus. ~100 pairs/day.

## Corpus Stats
- 734 pairs | avg entropy 4.48 bits | 7 domains | all PRESENT_2026 era

## Author
Steven Crawford-Maggard (EVEZ) — 2026
