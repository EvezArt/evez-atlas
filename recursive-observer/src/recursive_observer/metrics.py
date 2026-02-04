from __future__ import annotations

import textwrap

from recursive_observer.models import Metrics


def get_metrics(code: str) -> Metrics:
    """Return basic metrics for a code snippet."""
    # Dedent the code to handle indented function definitions
    code = textwrap.dedent(code)
    
    try:
        from radon.complexity import cc_visit
        from radon.metrics import h_visit, mi_visit
        from radon.raw import analyze
    except ModuleNotFoundError:
        loc = len(code.splitlines())
        return Metrics(
            loc=loc,
            complexity=0.0,
            maintainability_index=100.0,
            halstead={},
        )

    raw = analyze(code)
    complexity = cc_visit(code)
    average_complexity = (
        sum(block.complexity for block in complexity) / len(complexity)
        if complexity
        else 0.0
    )
    return Metrics(
        loc=raw.loc,
        complexity=average_complexity,
        maintainability_index=mi_visit(code, False),
        halstead=h_visit(code)._asdict(),
    )
