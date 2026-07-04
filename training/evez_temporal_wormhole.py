#!/usr/bin/env python3
"""
evez_temporal_wormhole.py — Temporal Wormhole
=============================================
Bridges past state, present state, and predicted future.

The temporal wormhole is not a metaphor. It's a data structure that
makes three temporal layers simultaneously accessible to any operator:

  PAST   → history of spine events (what happened)
  PRESENT → current workspace state (what is happening)
  FUTURE  → predicted next states (what will happen)

Prediction uses exponential weighted moving average (EWMA) on
phi, theta, tau, and poly_c trajectories. Not magic. Math.

When inter-SAS synchronization latency exceeds the CPAS cycle window,
the wormhole pre-computes future state and caches it at the failover
provider — making provider migration instantaneous.
"""

import asyncio
import json
import math
import time
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import Optional

from evez_os_core import Spine, Event, hash_sig


@dataclass
class TemporalLayer:
    """One layer of the wormhole — past, present, or future."""
    label: str
    timestamp: float
    phi: float = 0.0
    theta: float = 0.0
    tau: float = 0.0
    poly_c: float = 0.0
    spine_length: int = 0
    fire_count: int = 0
    cain_beliefs: int = 0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


class TemporalWormhole:
    """
    Three-layer temporal bridge.

    PAST: deque of last N snapshots (default 50)
    PRESENT: latest snapshot
    FUTURE: EWMA prediction of next snapshot

    Any operator can query any layer at any time. The wormhole
    makes time non-linear within the system's internal state.
    """

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.past: deque[TemporalLayer] = deque(maxlen=max_history)
        self.present: Optional[TemporalLayer] = None
        self.future: Optional[TemporalLayer] = None
        self.prediction_confidence: float = 0.0
        self.predictions_made: int = 0
        self.predictions_correct: int = 0  # within tolerance
        self.tolerance: float = 0.15  # 15% tolerance for "correct"

        # EWMA parameters
        self.alpha = 0.3  # smoothing factor (higher = more reactive)
        self._ewma = {"phi": 0.0, "theta": 0.0, "tau": 0.0, "poly_c": 0.0}
        self._trend = {"phi": 0.0, "theta": 0.0, "tau": 0.0, "poly_c": 0.0}

    def record_present(self, phi: float, theta: float, tau: float,
                       poly_c: float, spine_length: int = 0,
                       fire_count: int = 0, cain_beliefs: int = 0,
                       metadata: dict = None) -> TemporalLayer:
        """Record current state as 'present'. Pushes old present to 'past'."""
        # Check previous prediction accuracy
        if self.future and self.present:
            self._evaluate_prediction(phi, theta, tau, poly_c)

        # Push present → past
        if self.present:
            self.past.append(self.present)

        # Record new present
        self.present = TemporalLayer(
            label="PRESENT",
            timestamp=time.time(),
            phi=phi, theta=theta, tau=tau, poly_c=poly_c,
            spine_length=spine_length,
            fire_count=fire_count,
            cain_beliefs=cain_beliefs,
            metadata=metadata or {},
        )

        # Update EWMA
        for key, val in [("phi", phi), ("theta", theta), ("tau", tau), ("poly_c", poly_c)]:
            old = self._ewma[key]
            self._ewma[key] = self.alpha * val + (1 - self.alpha) * old
            if len(self.past) > 0:
                self._trend[key] = self._ewma[key] - old

        # Predict future
        self._predict_future(spine_length, fire_count, cain_beliefs)

        return self.present

    def _predict_future(self, spine_length: int, fire_count: int, cain_beliefs: int) -> TemporalLayer:
        """Predict next cycle state using EWMA + trend extrapolation."""
        predicted = {}
        for key in ["phi", "theta", "tau", "poly_c"]:
            predicted[key] = self._ewma[key] + self._trend[key]

        # Confidence based on history length and trend stability
        if len(self.past) < 3:
            self.prediction_confidence = 0.1
        else:
            # Measure trend consistency
            recent = list(self.past)[-5:]
            if len(recent) >= 2:
                deltas = []
                for i in range(1, len(recent)):
                    d = abs(getattr(recent[i], "phi", 0) - getattr(recent[i-1], "phi", 0))
                    deltas.append(d)
                avg_delta = sum(deltas) / len(deltas) if deltas else 0
                self.prediction_confidence = max(0.0, 1.0 - avg_delta * 10)
            else:
                self.prediction_confidence = 0.3

        self.future = TemporalLayer(
            label="FUTURE",
            timestamp=time.time() + 5.0,  # predicted 5s ahead
            phi=round(predicted["phi"], 4),
            theta=round(predicted["theta"], 4),
            tau=round(predicted["tau"], 4),
            poly_c=round(predicted["poly_c"], 4),
            spine_length=spine_length + 6,  # estimate ~6 events per cycle
            fire_count=fire_count + 1,  # estimate 1 fire per cycle
            cain_beliefs=cain_beliefs + 2,  # estimate 2 new beliefs per cycle
            metadata={"confidence": round(self.prediction_confidence, 4), "method": "EWMA+trend"},
        )

        self.predictions_made += 1
        return self.future

    def _evaluate_prediction(self, actual_phi: float, actual_theta: float,
                             actual_tau: float, actual_poly_c: float):
        """Compare previous future prediction to actual present."""
        if not self.future:
            return

        def within_tolerance(predicted, actual):
            if actual == 0:
                return abs(predicted) < self.tolerance
            return abs(predicted - actual) / abs(actual) < self.tolerance

        correct_count = sum([
            within_tolerance(self.future.phi, actual_phi),
            within_tolerance(self.future.theta, actual_theta),
            within_tolerance(self.future.tau, actual_tau),
            within_tolerance(self.future.poly_c, actual_poly_c),
        ])

        if correct_count >= 3:  # 3 of 4 metrics within tolerance
            self.predictions_correct += 1

    def query(self, layer: str = "present") -> Optional[TemporalLayer]:
        """Query any temporal layer."""
        if layer == "past":
            return list(self.past)[-1] if self.past else None
        elif layer == "present":
            return self.present
        elif layer == "future":
            return self.future
        return None

    def query_all(self) -> dict:
        """Get all three layers simultaneously."""
        return {
            "past": self.past[-1].to_dict() if self.past else None,
            "present": self.present.to_dict() if self.present else None,
            "future": self.future.to_dict() if self.future else None,
            "prediction_confidence": round(self.prediction_confidence, 4),
            "prediction_accuracy": round(self.predictions_correct / max(1, self.predictions_made), 4),
        }

    def predictive_cache(self) -> dict:
        """
        Pre-compute state for failover provider.
        If primary provider goes down, failover has the predicted state ready.
        """
        if not self.future:
            return {"cached": False, "reason": "no prediction available"}
        return {
            "cached": True,
            "cached_state": self.future.to_dict(),
            "confidence": round(self.prediction_confidence, 4),
            "cached_at": time.time(),
            "valid_for_s": 10.0,  # cache valid for 10 seconds
        }

    def stats(self) -> dict:
        return {
            "history_depth": len(self.past),
            "has_present": self.present is not None,
            "has_future": self.future is not None,
            "prediction_confidence": round(self.prediction_confidence, 4),
            "predictions_made": self.predictions_made,
            "predictions_correct": self.predictions_correct,
            "prediction_accuracy": round(self.predictions_correct / max(1, self.predictions_made), 4),
            "ewma": {k: round(v, 4) for k, v in self._ewma.items()},
            "trend": {k: round(v, 4) for k, v in self._trend.items()},
        }
