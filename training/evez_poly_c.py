#!/usr/bin/env python3
"""
evez_poly_c.py — EVEZ-OS poly_c Streaming Engine
=================================================
Continuous convergence metric computed from live circuit data.

poly_c is NOT a confidence score. It measures whether the system's
signal-generating mechanisms are converging — becoming redundant and
patterned — or diverging — scattered and novel.

  High poly_c → signals are coherent, model is crystallizing
  Low poly_c  → signals are scattered, anomaly mode

The formula (from EVEZ-OS architecture):

    poly_c = τ × ω × topo / (2 × √N)

Where:
  τ = FIRE threshold accumulator (how much cognitive fire has accumulated)
  ω = spine type diversity (how many distinct event types are active)
  topo = topological density (how interconnected the spine is)
  N = total event count (normalization factor)

This module computes poly_c every 500ms from live data, maintains a
trajectory, and triggers CAIN escalation when poly_c drops below threshold.

by Steven Crawford-Maggard (EVEZ) — 2026
"""

import json
import math
import time
import threading
from dataclasses import dataclass, field, asdict
from typing import Callable, Optional
from collections import defaultdict, deque
from enum import Enum


class ConvergenceMode(Enum):
    """System mode determined by poly_c level."""
    CONVERGENT = "convergent"    # poly_c > 3.5 — confident model
    STABLE = "stable"            # 2.0 ≤ poly_c ≤ 3.5 — normal operation
    ANOMALY = "anomaly"          # poly_c < 2.0 — scattered signals
    ESCALATION = "escalation"    # poly_c < 1.0 — CAIN escalation triggered


@dataclass
class PolyCReading:
    """A single poly_c measurement."""
    timestamp: float = field(default_factory=time.time)
    poly_c: float = 0.0
    tau: float = 0.0
    omega: float = 0.0          # type diversity
    topo: float = 0.0           # topological density
    n: int = 0                  # event count
    mode: str = "stable"
    rate_of_change: float = 0.0  # d(poly_c)/dt
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            raw = f"{self.timestamp}:{self.poly_c:.6f}:{self.n}"
            import hashlib
            self.hash = hashlib.sha256(raw.encode()).hexdigest()[:12]


class PolyCStreamer:
    """
    Continuous poly_c computation from live spine/circuit data.

    Usage:
        streamer = PolyCStreamer(supply_fn=lambda: {...})
        streamer.start()  # background thread, computes every 500ms
        reading = streamer.current()
        trajectory = streamer.trajectory(20)
        streamer.stop()
    """

    def __init__(self,
                 supply_fn: Optional[Callable] = None,
                 interval: float = 0.5,
                 convergent_threshold: float = 3.5,
                 anomaly_threshold: float = 2.0,
                 escalation_threshold: float = 1.0):
        """
        Args:
            supply_fn: function that returns current system metrics:
                {"tau": float, "event_types": list, "event_count": int, "density": float}
            interval: computation interval in seconds
        """
        self.supply_fn = supply_fn
        self.interval = interval
        self.convergent_threshold = convergent_threshold
        self.anomaly_threshold = anomaly_threshold
        self.escalation_threshold = escalation_threshold

        self.readings: deque = deque(maxlen=500)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.escalation_count = 0
        self.mode_history: deque = deque(maxlen=100)

    def start(self) -> None:
        """Start background computation."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop background computation."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run(self) -> None:
        """Background loop."""
        while self._running:
            self.compute()
            time.sleep(self.interval)

    def compute(self, data: Optional[dict] = None) -> PolyCReading:
        """
        Compute poly_c from supplied data or by calling supply_fn.

        poly_c = τ × ω × topo / (2 × √N)

        Returns a PolyCReading with mode and rate of change.
        """
        if data is None:
            if self.supply_fn:
                try:
                    data = self.supply_fn()
                except Exception:
                    data = {}
            else:
                data = {}

        tau = data.get("tau", 0.0)
        event_types = data.get("event_types", [])
        event_count = data.get("event_count", 0)
        density = data.get("density", 0.0)

        # ω = type diversity (normalized Shannon entropy of event type distribution)
        if event_types and event_count > 0:
            type_counts = defaultdict(int)
            for t in event_types:
                type_counts[t] += 1
            probs = [c / len(event_types) for c in type_counts.values()]
            omega = -sum(p * math.log2(p) for p in probs) if len(probs) > 1 else 0.0
        else:
            omega = 0.0

        # topo = topological density (given or computed from type diversity)
        topo = density if density > 0 else min(1.0, len(set(event_types)) / 10.0)

        # N = event count
        N = max(event_count, 1)

        # poly_c = τ × ω × topo / (2 × √N)
        poly_c = (tau * omega * topo) / (2.0 * math.sqrt(N))

        # Determine mode
        if poly_c > self.convergent_threshold:
            mode = ConvergenceMode.CONVERGENT
        elif poly_c > self.anomaly_threshold:
            mode = ConvergenceMode.STABLE
        elif poly_c > self.escalation_threshold:
            mode = ConvergenceMode.ANOMALY
        else:
            mode = ConvergenceMode.ESCALATION
            self.escalation_count += 1

        # Rate of change
        rate = 0.0
        with self._lock:
            if self.readings:
                prev = self.readings[-1]
                dt = max(time.time() - prev.timestamp, 0.001)
                rate = (poly_c - prev.poly_c) / dt

        reading = PolyCReading(
            poly_c=poly_c,
            tau=tau,
            omega=omega,
            topo=topo,
            n=N,
            mode=mode.value,
            rate_of_change=rate,
        )

        with self._lock:
            self.readings.append(reading)
            self.mode_history.append(mode.value)

        return reading

    def current(self) -> Optional[PolyCReading]:
        """Get the most recent reading."""
        return self.readings[-1] if self.readings else None

    def trajectory(self, n: int = 20) -> list:
        """Get the last n readings as dicts."""
        return [asdict(r) for r in list(self.readings)[-n:]]

    def mode_distribution(self) -> dict:
        """Distribution of modes over history."""
        if not self.mode_history:
            return {}
        counts = defaultdict(int)
        for m in self.mode_history:
            counts[m] += 1
        total = len(self.mode_history)
        return {m: round(c / total, 4) for m, c in sorted(counts.items())}

    def is_convergent(self) -> bool:
        """True if system is in convergent mode."""
        r = self.current()
        return r is not None and r.mode == ConvergenceMode.CONVERGENT.value

    def needs_escalation(self) -> bool:
        """True if CAIN escalation should be triggered."""
        r = self.current()
        return r is not None and r.mode == ConvergenceMode.ESCALATION.value

    def summary(self) -> dict:
        """Full summary for logging."""
        r = self.current()
        return {
            "current_poly_c": r.poly_c if r else None,
            "current_mode": r.mode if r else None,
            "rate_of_change": r.rate_of_change if r else None,
            "total_readings": len(self.readings),
            "escalations": self.escalation_count,
            "mode_distribution": self.mode_distribution(),
            "convergent": self.is_convergent(),
            "needs_escalation": self.needs_escalation(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("═" * 70)
    print("EVEZ-OS poly_c STREAMING ENGINE — Self Test")
    print("═" * 70)

    streamer = PolyCStreamer(
        interval=0.1,
        convergent_threshold=3.5,
        anomaly_threshold=2.0,
    )

    # Test 1: Convergent system (high τ, diverse types, high density)
    print("\n[TEST 1] Convergent system (high τ, diverse types)...")
    reading = streamer.compute({
        "tau": 22.0,
        "event_types": ["oracle_pulse", "cross_domain", "fire_event",
                        "cain_audit", "broadcast", "heartbeat", "evolve", "code_artifact"],
        "event_count": 500,
        "density": 0.89,
    })
    print(f"  poly_c = {reading.poly_c:.4f} → mode = {reading.mode}")
    print(f"  ω = {reading.omega:.4f} (type diversity)")
    print(f"  topo = {reading.topo:.4f} (density)")

    # Test 2: Stable system (moderate values)
    print("\n[TEST 2] Stable system (moderate values)...")
    reading = streamer.compute({
        "tau": 15.0,
        "event_types": ["oracle_pulse", "cross_domain", "fire_event", "cain_audit"],
        "event_count": 100,
        "density": 0.5,
    })
    print(f"  poly_c = {reading.poly_c:.4f} → mode = {reading.mode}")

    # Test 3: Anomaly (low τ, few types)
    print("\n[TEST 3] Anomaly (low τ, few types)...")
    reading = streamer.compute({
        "tau": 3.0,
        "event_types": ["heartbeat"],
        "event_count": 5,
        "density": 0.1,
    })
    print(f"  poly_c = {reading.poly_c:.4f} → mode = {reading.mode}")
    print(f"  Needs escalation: {streamer.needs_escalation()}")

    # Trajectory
    print(f"\n[TRAJECTORY] Last {len(streamer.readings)} readings:")
    for r in streamer.trajectory(10):
        print(f"  t={r['timestamp']:.2f} poly_c={r['poly_c']:.4f} mode={r['mode']} d/dt={r['rate_of_change']:.4f}")

    # Mode distribution
    print(f"\n[MODE DISTRIBUTION] {streamer.mode_distribution()}")

    # Background thread test
    print("\n[TEST 4] Background thread (5 readings at 0.1s)...")
    supply_data = {"tau": 18.0, "event_types": ["a","b","c","d","e","f"], "event_count": 200, "density": 0.75}
    streamer2 = PolyCStreamer(supply_fn=lambda: supply_data, interval=0.1)
    streamer2.start()
    time.sleep(0.55)
    streamer2.stop()
    print(f"  Readings: {len(streamer2.readings)}")
    r = streamer2.current()
    if r:
        print(f"  Final: poly_c={r.poly_c:.4f} mode={r.mode}")

    print(f"\n[SUMMARY] {json.dumps(streamer2.summary(), indent=2)}")

    print("\n✓ poly_c Streaming Engine operational")
