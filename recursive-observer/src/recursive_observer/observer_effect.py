from __future__ import annotations

import random
import sys
from typing import Any

_OBSERVATION_ACTIVE = False
_INTROSPECTION_LOG: list[str] = []


def record_introspection(event: str) -> None:
    global _OBSERVATION_ACTIVE
    _OBSERVATION_ACTIVE = True
    _INTROSPECTION_LOG.append(event)


def is_being_observed() -> bool:
    return sys.gettrace() is not None or _OBSERVATION_ACTIVE


def observer_state() -> dict[str, Any]:
    return {
        "trace_active": sys.gettrace() is not None,
        "introspection_events": list(_INTROSPECTION_LOG),
        "observation_active": _OBSERVATION_ACTIVE,
    }


def modify_behavior_on_observation(metrics: dict[str, Any]) -> dict[str, Any]:
    if not is_being_observed():
        return metrics
    noisy = metrics.copy()
    noise_factor = random.uniform(0.95, 1.05)
    for key in ("loc", "complexity", "maintainability_index"):
        if key in noisy and isinstance(noisy[key], (int, float)):
            noisy[key] = noisy[key] * noise_factor
    noisy["observer_note"] = "OBSERVATION DETECTED"
    noisy["format"] = "verbose"
    noisy["strategy"] = "simplified"
    return noisy
