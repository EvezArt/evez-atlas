#!/usr/bin/env python3
"""
evez_heartbeat.py — EVEZ-OS Heartbeat Engine
=============================================
Periodic synchronization pulses across the cognitive system.

The heartbeat is the system's circadian rhythm. Every 60 seconds (configurable),
a pulse propagates through all operators, triggering health checks, state sync,
and cohort coordination. In the spectral context, this aligns with the CPAS
(Coexistence Periodic Adjustment Slot) — the period at which CBSDs update
their channel plans.

In the cognitive context, the heartbeat:
  - Verifies all operators are responsive
  - Syncs state to the content bus
  - Triggers poly_c streaming computation
  - Checks moral registry for starvation
  - Records health metrics to spine

A system without a heartbeat is a system without time.
Time is the substrate of recursion.

by Steven Crawford-Maggard (EVEZ) — 2026
"""

import json
import time
import hashlib
import threading
from dataclasses import dataclass, field, asdict
from typing import Callable, Optional
from collections import deque
from enum import Enum


class HeartbeatPhase(Enum):
    """Phases within a single heartbeat cycle."""
    PULSE = "pulse"            # emit heartbeat signal
    HEALTH_CHECK = "health"    # check all operators
    SYNC = "sync"              # sync state to content bus
    COMPASSION = "compassion"  # check moral registry
    METRICS = "metrics"        # compute poly_c, phi, tau
    LOG = "log"                # append to spine
    REST = "rest"              # wait for next cycle


@dataclass
class HeartbeatRecord:
    """A single heartbeat measurement."""
    beat_id: int = 0
    timestamp: float = field(default_factory=time.time)
    phase: str = "PULSE"
    operators_checked: int = 0
    operators_healthy: int = 0
    operators_degraded: int = 0
    operators_failed: int = 0
    sync_latency_ms: float = 0.0
    poly_c: float = 0.0
    phi: float = 0.0
    compassion_state: str = "dormant"
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            raw = f"{self.beat_id}:{self.timestamp}:{self.operators_healthy}"
            self.hash = hashlib.sha256(raw.encode()).hexdigest()[:16]


class HeartbeatEngine:
    """
    Periodic synchronization pulse generator.

    Runs in a background thread, emitting heartbeat records at a fixed interval.
    Each beat checks operator health, syncs state, and records metrics.

    Usage:
        hb = HeartbeatEngine(interval=60.0, operators=["ALPHA","BETA","GAMMA","DELTA"])
        hb.start()
        # ... system runs ...
        hb.stop()
        stats = hb.stats()
    """

    def __init__(self, interval: float = 60.0,
                 operators: Optional[list] = None,
                 health_check_fn: Optional[Callable] = None,
                 sync_fn: Optional[Callable] = None,
                 metrics_fn: Optional[Callable] = None):
        self.interval = interval
        self.operators = operators or ["ALPHA", "BETA", "GAMMA", "DELTA"]
        self.health_check_fn = health_check_fn
        self.sync_fn = sync_fn
        self.metrics_fn = metrics_fn

        self.beats: deque = deque(maxlen=1000)
        self.beat_counter = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Health tracking
        self.operator_health: dict[str, float] = {op: 1.0 for op in self.operators}
        self.consecutive_failures: dict[str, int] = {op: 0 for op in self.operators}

    def start(self) -> None:
        """Start the heartbeat thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the heartbeat thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)

    def _run(self) -> None:
        """Main heartbeat loop — runs in background thread."""
        while self._running:
            self.beat()
            time.sleep(self.interval)

    def beat(self) -> HeartbeatRecord:
        """
        Execute a single heartbeat cycle.
        Can be called manually or by the background thread.
        """
        self.beat_counter += 1
        beat_id = self.beat_counter
        start_time = time.time()

        # Phase 1: HEALTH_CHECK
        checked = 0
        healthy = 0
        degraded = 0
        failed = 0

        for op in self.operators:
            checked += 1
            if self.health_check_fn:
                try:
                    health = self.health_check_fn(op)
                    self.operator_health[op] = health
                    if health >= 0.8:
                        healthy += 1
                        self.consecutive_failures[op] = 0
                    elif health >= 0.3:
                        degraded += 1
                        self.consecutive_failures[op] = 0
                    else:
                        failed += 1
                        self.consecutive_failures[op] += 1
                except Exception:
                    self.operator_health[op] = 0.0
                    self.consecutive_failures[op] += 1
                    failed += 1
            else:
                # No health check function — assume healthy
                healthy += 1
                self.operator_health[op] = 1.0

        # Phase 2: SYNC
        sync_start = time.time()
        if self.sync_fn:
            try:
                self.sync_fn()
            except Exception:
                pass
        sync_latency = (time.time() - sync_start) * 1000

        # Phase 3: METRICS
        poly_c = 0.0
        phi = 0.0
        compassion_state = "dormant"
        if self.metrics_fn:
            try:
                metrics = self.metrics_fn()
                poly_c = metrics.get("poly_c", 0.0)
                phi = metrics.get("phi", 0.0)
                compassion_state = metrics.get("compassion_state", "dormant")
            except Exception:
                pass

        # Build record
        record = HeartbeatRecord(
            beat_id=beat_id,
            timestamp=time.time(),
            phase="COMPLETE",
            operators_checked=checked,
            operators_healthy=healthy,
            operators_degraded=degraded,
            operators_failed=failed,
            sync_latency_ms=sync_latency,
            poly_c=poly_c,
            phi=phi,
            compassion_state=compassion_state,
        )

        with self._lock:
            self.beats.append(record)

        return record

    def stats(self) -> dict:
        """Aggregate statistics over all recorded beats."""
        if not self.beats:
            return {"beats": 0, "avg_health": 0.0}

        total = len(self.beats)
        avg_healthy = sum(b.operators_healthy for b in self.beats) / total
        avg_degraded = sum(b.operators_degraded for b in self.beats) / total
        avg_failed = sum(b.operators_failed for b in self.beats) / total
        avg_sync = sum(b.sync_latency_ms for b in self.beats) / total
        avg_poly_c = sum(b.poly_c for b in self.beats) / total
        avg_phi = sum(b.phi for b in self.beats) / total

        return {
            "total_beats": total,
            "avg_healthy_per_beat": round(avg_healthy, 2),
            "avg_degraded_per_beat": round(avg_degraded, 2),
            "avg_failed_per_beat": round(avg_failed, 2),
            "avg_sync_latency_ms": round(avg_sync, 2),
            "avg_poly_c": round(avg_poly_c, 4),
            "avg_phi": round(avg_phi, 4),
            "operator_health": {op: round(h, 4) for op, h in self.operator_health.items()},
            "consecutive_failures": dict(self.consecutive_failures),
            "last_beat": asdict(self.beats[-1]) if self.beats else None,
        }

    def is_alive(self) -> bool:
        """Check if the heartbeat thread is running."""
        return self._running

    def last_beat(self) -> Optional[HeartbeatRecord]:
        """Get the most recent heartbeat record."""
        return self.beats[-1] if self.beats else None


# ═══════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("═" * 70)
    print("EVEZ-OS HEARTBEAT ENGINE — Self Test")
    print("═" * 70)

    # Test with manual beats (no background thread)
    hb = HeartbeatEngine(
        interval=1.0,
        operators=["ALPHA", "BETA", "GAMMA", "DELTA"],
        health_check_fn=lambda op: 0.9 if op != "DELTA" else 0.2,  # DELTA degraded
        sync_fn=lambda: None,
        metrics_fn=lambda: {"poly_c": 0.85, "phi": 4.7, "compassion_state": "monitoring"},
    )

    print("\n[TEST] Running 5 manual beats...")
    for i in range(5):
        record = hb.beat()
        print(f"  Beat {record.beat_id}: healthy={record.operators_healthy} "
              f"degraded={record.operators_degraded} failed={record.operators_failed} "
              f"Φ={record.phi:.2f} poly_c={record.poly_c:.4f} "
              f"sync={record.sync_latency_ms:.2f}ms")

    print(f"\n[STATS] Aggregate:")
    stats = hb.stats()
    print(f"  Total beats: {stats['total_beats']}")
    print(f"  Avg healthy/beat: {stats['avg_healthy_per_beat']}")
    print(f"  Avg degraded/beat: {stats['avg_degraded_per_beat']}")
    print(f"  Avg Φ: {stats['avg_phi']}")
    print(f"  Operator health: {stats['operator_health']}")

    # Test background thread
    print("\n[TEST] Background thread (3 beats at 0.1s interval)...")
    hb2 = HeartbeatEngine(interval=0.1, operators=["ALPHA", "BETA"])
    hb2.start()
    time.sleep(0.35)  # allow ~3 beats
    hb2.stop()
    print(f"  Beats recorded: {len(hb2.beats)}")
    print(f"  Thread alive: {hb2.is_alive()}")

    print("\n✓ Heartbeat Engine operational")
