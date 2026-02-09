from __future__ import annotations

import sys
import time
from types import FrameType
from typing import Any, Callable

from recursive_observer.models import RuntimeTrace


# Global lifecycle event tracker for root trace
_lifecycle_events: list[dict[str, Any]] = []


def record_lifecycle_event(event_type: str, entity_id: str, state: str, metadata: dict[str, Any] | None = None):
    """Record a lifecycle event at the root trace level.
    
    This creates a deeper connection between entity lifecycle and execution traces.
    """
    event = {
        'timestamp': time.time(),
        'event_type': event_type,
        'entity_id': entity_id,
        'state': state,
        'metadata': metadata or {}
    }
    _lifecycle_events.append(event)


def get_lifecycle_events() -> list[dict[str, Any]]:
    """Get all recorded lifecycle events."""
    return _lifecycle_events.copy()


def clear_lifecycle_events():
    """Clear all lifecycle events."""
    _lifecycle_events.clear()


def trace_execution(target: Callable[..., Any], *args: Any, **kwargs: Any) -> RuntimeTrace:
    if sys.gettrace() is not None:
        raise RuntimeError("Tracer already active")

    events: list[tuple[str, int, str]] = []
    timing: dict[str, float] = {}
    variable_snapshots: list[dict[str, Any]] = []
    start_times: dict[int, float] = {}
    
    # Clear lifecycle events before starting trace to capture only events during execution
    clear_lifecycle_events()

    def tracer(frame: FrameType, event: str, arg: Any):
        if event not in {"call", "return"}:
            return tracer
        func_name = frame.f_code.co_name
        events.append((func_name, frame.f_lineno, event))
        if event == "call":
            start_times[id(frame)] = time.perf_counter()
        elif event == "return":
            start = start_times.pop(id(frame), None)
            if start is not None:
                timing[func_name] = timing.get(func_name, 0.0) + (time.perf_counter() - start)
        variable_snapshots.append({
            "function": func_name,
            "event": event,
            "locals": dict(frame.f_locals),
        })
        return tracer

    sys.settrace(tracer)
    try:
        target(*args, **kwargs)
    finally:
        sys.settrace(None)
    
    # Capture lifecycle events that occurred during execution
    lifecycle_snapshot = get_lifecycle_events()

    return RuntimeTrace(
        events=events, 
        timing=timing, 
        variable_snapshots=variable_snapshots,
        lifecycle_events=lifecycle_snapshot
    )
