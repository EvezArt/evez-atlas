from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ProgramStructure:
    ast_dump: str
    functions: list[str]
    classes: list[str]
    imports: list[str]


@dataclass
class Metrics:
    loc: int
    complexity: float
    maintainability_index: float
    halstead: dict[str, Any]


@dataclass
class RuntimeTrace:
    events: list[tuple[str, int, str]]
    timing: dict[str, float]
    variable_snapshots: list[dict[str, Any]]
    lifecycle_events: list[dict[str, Any]] | None = None  # Track entity lifecycle events


@dataclass
class MeasurementSnapshot:
    iteration: int
    metrics: Metrics
    observer_state: dict[str, Any]
    timestamp: datetime


@dataclass
class ConvergenceReport:
    snapshots: list[MeasurementSnapshot]
    converged: bool
    final_delta: float
