"""Compatibility wrapper exposing retry helper for cross-module imports."""

from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def retry_with_backoff(fn: Callable[[], T], retries: int = 4, base_delay: float = 1.0) -> T:
    """Run callable with exponential backoff and retry semantics."""
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(base_delay * (2**attempt))
    assert last_exc is not None
    raise last_exc
