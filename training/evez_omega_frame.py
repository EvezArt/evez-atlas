#!/usr/bin/env python3
"""
evez_omega_frame.py — EVEZ-OS Omega Frame
==========================================
Real-time navigable coordinate map for internal state.

The Omega Frame projects the system's internal state (Φ, θ, τ, spine density,
operator outputs, CAIN beliefs, FIRE events) into a navigable N-dimensional
coordinate space. Any agent or operator can query the frame to get a spatial
representation of where the system "is" right now — and where it's trending.

This is not visualization. This is a coordinate system for cognition.
The frame enables:
  - Distance metrics between current state and target state
  - Velocity vectors (rate of change of state)
  - Anomaly detection (sudden jumps in coordinate space)
  - Navigation (operators can steer toward target coordinates)

by Steven Crawford-Maggard (EVEZ) — 2026
"""

import json
import math
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional
from collections import deque


@dataclass
class StateVector:
    """A point in Omega Frame coordinate space."""
    phi: float = 0.0              # integrated information
    theta: float = 45.0           # theta-shift angle (degrees)
    tau: float = 0.0              # FIRE threshold accumulator
    spine_density: float = 0.0    # normalized entropy of spine event types
    spine_length: int = 0         # total events
    gnw_confidence: float = 0.0   # GNW binding confidence
    cain_contradictions: int = 0  # active contradictions
    fire_count: int = 0           # total FIRE events
    operator_health: float = 1.0  # 1.0 = all operators healthy
    timestamp: float = field(default_factory=time.time)

    def to_tuple(self) -> tuple:
        """Convert to ordered tuple for distance calculations."""
        return (self.phi, self.theta / 90.0, self.tau / 25.0,
                self.spine_density, self.spine_length / 1000.0,
                self.gnw_confidence, self.cain_contradictions / 10.0,
                self.fire_count / 50.0, self.operator_health)

    def to_dict(self) -> dict:
        return asdict(self)


class OmegaFrame:
    """
    Navigable coordinate map for EVEZ-OS internal state.

    Maintains a sliding window of StateVectors and provides:
      - Current position in state space
      - Velocity (rate of change)
      - Distance to target state
      - Anomaly detection (Mahalanobis-style distance from historical mean)
      - Navigation suggestions (which dimension to adjust to reach target)
    """

    def __init__(self, window_size: int = 100, target: Optional[StateVector] = None):
        self.window_size = window_size
        self.history: deque = deque(maxlen=window_size)
        self.target = target or StateVector(
            phi=5.0, theta=45.0, tau=22.0,
            spine_density=0.9, spine_length=500,
            gnw_confidence=0.8, cain_contradictions=0,
            fire_count=20, operator_health=1.0
        )
        self._velocity_cache = None
        self._last_update = 0.0

    def update(self, vector: StateVector) -> None:
        """Record a new state vector. Called every cognitive cycle."""
        self.history.append(vector)
        self._last_update = vector.timestamp
        self._velocity_cache = None  # invalidate cache

    @property
    def current(self) -> Optional[StateVector]:
        """Get the most recent state vector."""
        return self.history[-1] if self.history else None

    @property
    def velocity(self) -> Optional[StateVector]:
        """
        Rate of change between last two state vectors.
        Positive velocity = moving toward higher values.
        """
        if len(self.history) < 2:
            return None
        if self._velocity_cache is not None:
            return self._velocity_cache

        curr = self.history[-1]
        prev = self.history[-2]
        dt = max(curr.timestamp - prev.timestamp, 0.001)

        vel = StateVector(
            phi=(curr.phi - prev.phi) / dt,
            theta=(curr.theta - prev.theta) / dt,
            tau=(curr.tau - prev.tau) / dt,
            spine_density=(curr.spine_density - prev.spine_density) / dt,
            spine_length=int((curr.spine_length - prev.spine_length) / dt),
            gnw_confidence=(curr.gnw_confidence - prev.gnw_confidence) / dt,
            cain_contradictions=int((curr.cain_contradictions - prev.cain_contradictions) / dt),
            fire_count=int((curr.fire_count - prev.fire_count) / dt),
            operator_health=(curr.operator_health - prev.operator_health) / dt,
        )
        self._velocity_cache = vel
        return vel

    def distance_to_target(self) -> float:
        """
        Euclidean distance from current state to target state.
        Lower = closer to desired operating point.
        """
        if not self.history:
            return float('inf')
        curr = self.history[-1].to_tuple()
        tgt = self.target.to_tuple()
        return math.sqrt(sum((c - t) ** 2 for c, t in zip(curr, tgt)))

    def anomaly_score(self) -> float:
        """
        How far the current state is from the historical mean.
        Uses normalized Euclidean distance. >2.0 = anomalous.
        """
        if len(self.history) < 5:
            return 0.0

        curr = self.history[-1].to_tuple()
        n_dims = len(curr)

        # Compute mean and std for each dimension
        cols = list(zip(*[v.to_tuple() for v in self.history]))
        means = [sum(c) / len(c) for c in cols]
        stds = [max(math.sqrt(sum((x - m) ** 2 for x in c) / len(c)), 1e-6) for c, m in zip(cols, means)]

        # Normalized distance
        return math.sqrt(sum(((c - m) / s) ** 2 for c, m, s in zip(curr, means, stds)) / n_dims)

    def navigation_suggestion(self) -> dict:
        """
        Suggest which dimension to adjust to close distance to target.
        Returns the dimension with largest gap and its sign.
        """
        if not self.history:
            return {"dimension": "none", "gap": 0.0, "direction": "none"}

        curr = self.history[-1].to_tuple()
        tgt = self.target.to_tuple()
        dims = ["phi", "theta", "tau", "spine_density", "spine_length",
                "gnw_confidence", "cain_contradictions", "fire_count", "operator_health"]

        gaps = [(dims[i], tgt[i] - curr[i]) for i in range(len(dims))]
        gaps.sort(key=lambda x: abs(x[1]), reverse=True)

        dim, gap = gaps[0]
        return {
            "dimension": dim,
            "gap": round(gap, 4),
            "direction": "increase" if gap > 0 else "decrease",
            "current": round(curr[dims.index(dim)], 4),
            "target": round(tgt[dims.index(dim)], 4),
        }

    def trajectory(self, n: int = 10) -> list:
        """Return the last n state vectors for trajectory analysis."""
        return [v.to_dict() for v in list(self.history)[-n:]]

    def summary(self) -> dict:
        """Full summary for logging/dashboard."""
        curr = self.current
        vel = self.velocity
        return {
            "current": curr.to_dict() if curr else None,
            "velocity": vel.to_dict() if vel else None,
            "distance_to_target": round(self.distance_to_target(), 4),
            "anomaly_score": round(self.anomaly_score(), 4),
            "navigation": self.navigation_suggestion(),
            "history_length": len(self.history),
            "target": self.target.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.summary(), indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("═" * 70)
    print("EVEZ-OS OMEGA FRAME — Self Test")
    print("═" * 70)

    frame = OmegaFrame(window_size=50)

    # Simulate 10 cognitive cycles with varying state
    print("\n[TEST] Simulating 10 cycles...")
    for i in range(10):
        vec = StateVector(
            phi=4.0 + i * 0.1,
            theta=45.0 + math.sin(i) * 5,
            tau=18.0 + i * 0.4,
            spine_density=0.7 + i * 0.02,
            spine_length=6 * (i + 1),
            gnw_confidence=0.05 * i,
            cain_contradictions=0,
            fire_count=i,
            operator_health=1.0,
        )
        frame.update(vec)

    print(f"  Current position: Φ={frame.current.phi:.2f} θ={frame.current.theta:.1f}° τ={frame.current.tau:.2f}")
    print(f"  Velocity: dΦ/dt={frame.velocity.phi:.4f} dτ/dt={frame.velocity.tau:.4f}")
    print(f"  Distance to target: {frame.distance_to_target():.4f}")
    print(f"  Anomaly score: {frame.anomaly_score():.4f}")
    print(f"  Navigation: {frame.navigation_suggestion()}")

    # Inject anomaly
    print("\n[TEST] Injecting anomaly (sudden Φ drop)...")
    frame.update(StateVector(
        phi=0.5, theta=80.0, tau=5.0,
        spine_density=0.2, spine_length=60,
        gnw_confidence=0.0, cain_contradictions=5,
        fire_count=10, operator_health=0.6
    ))
    print(f"  Anomaly score after injection: {frame.anomaly_score():.4f} (>2.0 = anomalous)")
    print(f"  Navigation: {frame.navigation_suggestion()}")

    # Export
    print(f"\n[EXPORT] JSON summary:")
    print(frame.to_json())

    print("\n✓ Omega Frame operational")
