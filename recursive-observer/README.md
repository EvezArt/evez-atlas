# Recursive Observer

> "A program that watches programs. When it watches itself, it changes. When it changes, the measurement changes. The recursion continues until nothing more shifts—**measurement collapse**. This is the observer effect, written in Python."

## ⚠️ Big Disclaimer

This is a **conceptual demonstration of self-referential measurement and the observer effect metaphor. Not for production use.** It is intentionally experimental and emphasizes safe, reversible transformations.

## What It Does

- Measures other programs (structure, metrics, dependencies, runtime state).
- Measures itself with the same machinery.
- Modifies behavior when it detects observation.
- Recursively measures until metrics stabilize, including a pass that measures the tracer itself.
- Performs safe, reversible AST transformations.

## Architecture

```
┌────────────────────┐
│  Target Program    │
└─────────┬──────────┘
          │ measure
          ▼
┌────────────────────┐
│  Introspector      │─────┐
└─────────┬──────────┘     │ observes
          │ self-measure    ▼
          ▼          ┌────────────────────┐
┌────────────────────┐  │ Observer Effect │
│ Recursive Engine   │◀─┤  (behavior shift)│
└─────────┬──────────┘  └────────────────────┘
          │ repeat
          ▼
┌────────────────────┐
│  Stabilized Metrics│
└────────────────────┘
```

## Example Output

```
Converged after 3 iterations
Final delta: 0.0
```

## Glossary

- **Observer effect**: A metaphor here for changing output when a measurement is detected.
- **Measurement collapse**: Repeating observation until changes stabilize.
- **Self-measurement**: Using the same analysis tools on the analyzer itself.

## CLI Usage

```bash
recursive-observer analyze --target path/to/script.py --output metrics.json
recursive-observer self-analyze --output self_metrics.json
recursive-observer collapse --target script.py --max-iter 10 --tolerance 0.01
recursive-observer trace --target script.py --function main --args '["arg1"]'
recursive-observer transform --input script.py --output traced_script.py --add-traces
recursive-observer observe --target script.py --show-behavior-change
```

## Safety Constraints

- No arbitrary code execution from untrusted sources.
- No network operations or privilege escalation.
- Self-modification limited to safe AST rewrites (logging, renaming, hooks).
- Original sources preserved via `.original` backups.
