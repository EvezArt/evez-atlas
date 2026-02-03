from __future__ import annotations

import copy
import inspect
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from recursive_observer.introspect import get_metrics as calculate_metrics
from recursive_observer.models import ConvergenceReport, MeasurementSnapshot, Metrics
from recursive_observer.observer_effect import modify_behavior_on_observation, observer_state
from recursive_observer.tracer import trace_execution


def _metrics_to_dict(metrics: Metrics) -> dict[str, Any]:
    return {
        "loc": metrics.loc,
        "complexity": metrics.complexity,
        "maintainability_index": metrics.maintainability_index,
        "halstead": metrics.halstead,
    }


def _delta(a: Metrics, b: Metrics) -> float:
    return abs(a.complexity - b.complexity) + abs(a.loc - b.loc)


def _code_for_target(target: Callable[..., Any] | str | Path) -> str:
    if callable(target):
        return inspect.getsource(target)
    return Path(target).read_text(encoding="utf-8")


def measure_until_stable(
    target: Callable[..., Any] | str | Path,
    max_iterations: int = 10,
    tolerance: float = 0.01,
) -> ConvergenceReport:
    snapshots: list[MeasurementSnapshot] = []
    previous_metrics: Metrics | None = None

    for iteration in range(max_iterations):
        if iteration == 2:
            code = inspect.getsource(trace_execution)
        else:
            code = _code_for_target(target)
        metrics = calculate_metrics(code)

        if iteration == 1 and callable(target):
            trace_execution(target)

        metrics_dict = _metrics_to_dict(metrics)
        adjusted = modify_behavior_on_observation(metrics_dict)
        metrics = Metrics(
            loc=int(adjusted["loc"]),
            complexity=float(adjusted["complexity"]),
            maintainability_index=float(adjusted["maintainability_index"]),
            halstead=copy.deepcopy(metrics.halstead),
        )

        snapshots.append(
            MeasurementSnapshot(
                iteration=iteration,
                metrics=metrics,
                observer_state=observer_state(),
                timestamp=datetime.now(timezone.utc),
            )
        )

        if previous_metrics is not None:
            delta = _delta(previous_metrics, metrics)
            if delta <= tolerance:
                return ConvergenceReport(
                    snapshots=snapshots,
                    converged=True,
                    final_delta=delta,
                )
        previous_metrics = metrics

    final_delta = _delta(previous_metrics, previous_metrics) if previous_metrics else 0.0
    return ConvergenceReport(snapshots=snapshots, converged=False, final_delta=final_delta)


def recursive_self_measure(
    target: Callable[..., Any] | str | Path | None = None, depth: int = 3
) -> list[MeasurementSnapshot]:
    snapshots: list[MeasurementSnapshot] = []

    def measure_layer(layer: int, target: Callable[..., Any] | str | Path) -> None:
        metrics = calculate_metrics(_code_for_target(target))
        snapshots.append(
            MeasurementSnapshot(
                iteration=layer,
                metrics=metrics,
                observer_state=observer_state(),
                timestamp=datetime.now(timezone.utc),
            )
        )
        if layer + 1 < depth:
            measure_layer(layer + 1, measure_layer)

    seed_target = target or measure_layer
    measure_layer(0, seed_target)
    return snapshots
