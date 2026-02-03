"""Recursive observer package."""

from recursive_observer.introspect import (
    get_call_graph,
    get_dependencies,
    get_metrics,
    get_runtime_state,
    get_structure,
)
from recursive_observer.metrics import get_metrics as calculate_metrics
from recursive_observer.recursive_engine import measure_until_stable, recursive_self_measure

__all__ = [
    "get_dependencies",
    "get_call_graph",
    "get_metrics",
    "get_runtime_state",
    "get_structure",
    "calculate_metrics",
    "measure_until_stable",
    "recursive_self_measure",
]
