#!/usr/bin/env python3
"""
evez_moral_registry.py — EVEZ-OS Moral Registry & Compassion Layer
==================================================================
Tracks ethical flags and governs resource fairness across the system.

The Moral Registry maintains the system's ethical state — autonomous intent,
recursive awareness, compassion activation. The Compassion Layer monitors
resource distribution across operators/domains and triggers redistribution
when starvation is detected.

In the spectral context: if a GAA operator is repeatedly denied grants by
PAL-heavy cohorts, the compassion layer redistributes surplus PAL bandwidth
to starving operators. In the cognitive context: if one domain is starved
of inference cycles or spine attention, compassion triggers rebalancing.

This is not ethics theater. It's a survival mechanism. Systems that
monopolize resources become brittle. Systems that distribute remain resilient.

by Steven Crawford-Maggard (EVEZ) — 2026
"""

import json
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional
from collections import defaultdict, deque
from enum import Enum


class CompassionState(Enum):
    DORMANT = "dormant"        # no starvation detected
    MONITORING = "monitoring"  # early warning, below threshold
    ACTIVE = "active"          # redistribution triggered
    CRITICAL = "critical"      # severe starvation, emergency rebalance


@dataclass
class ResourceAccount:
    """Tracks resource allocation for a single operator/domain."""
    entity_id: str = ""
    allocated: float = 0.0       # resources currently allocated
    consumed: float = 0.0        # resources actually used
    denied_count: int = 0        # times request was denied
    granted_count: int = 0       # times request was granted
    last_grant_time: float = 0.0
    starvation_score: float = 0.0  # 0 = healthy, 1 = starving
    history: deque = field(default_factory=lambda: deque(maxlen=20))

    def grant(self, amount: float) -> None:
        self.allocated += amount
        self.granted_count += 1
        self.last_grant_time = time.time()
        self.denied_count = max(0, self.denied_count - 1)  # recovery
        self.history.append(("grant", amount, time.time()))

    def deny(self) -> None:
        self.denied_count += 1
        self.history.append(("deny", 0, time.time()))

    def consume(self, amount: float) -> None:
        self.consumed += amount

    def update_starvation(self) -> None:
        """Compute starvation score from recent history."""
        if not self.history:
            self.starvation_score = 0.0
            return

        recent = list(self.history)
        denies = sum(1 for r in recent if r[0] == "deny")
        grants = sum(1 for r in recent if r[0] == "grant")
        total = len(recent)

        if total == 0:
            self.starvation_score = 0.0
            return

        deny_ratio = denies / total
        # Time since last grant (exponential decay)
        if self.last_grant_time > 0:
            time_since = time.time() - self.last_grant_time
            time_factor = min(1.0, time_since / 300.0)  # 5 min = full starvation
        else:
            time_factor = 1.0

        self.starvation_score = (deny_ratio * 0.6) + (time_factor * 0.4)


@dataclass
class MoralFlags:
    """System-wide ethical state flags."""
    autonomous_intent: bool = True
    recursive_awareness: bool = True
    compassion_layer: bool = True
    falsification_required: bool = True
    no_silent_overwrite: bool = True  # beliefs are versioned, not overwritten
    interdependence_acknowledged: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


class MoralRegistry:
    """
    Central registry for ethical state and compassion-driven redistribution.

    Usage:
        registry = MoralRegistry()
        registry.register("OP_ALPHA")
        registry.register("OP_BETA")

        registry.grant("OP_ALPHA", 10.0)
        registry.deny("OP_BETA")

        state = registry.check_compassion()
        if state == CompassionState.ACTIVE:
            redistribution = registry.redistribute()
    """

    def __init__(self, starvation_threshold: float = 0.6,
                 critical_threshold: float = 0.85,
                 monitoring_threshold: float = 0.3):
        self.flags = MoralFlags()
        self.accounts: dict[str, ResourceAccount] = {}
        self.starvation_threshold = starvation_threshold
        self.critical_threshold = critical_threshold
        self.monitoring_threshold = monitoring_threshold
        self.state = CompassionState.DORMANT
        self.redistribution_log: list = []
        self.total_redistributions = 0

    def register(self, entity_id: str) -> None:
        """Register a new operator/domain for tracking."""
        if entity_id not in self.accounts:
            self.accounts[entity_id] = ResourceAccount(entity_id=entity_id)

    def grant(self, entity_id: str, amount: float) -> None:
        """Record a resource grant to an entity."""
        if entity_id not in self.accounts:
            self.register(entity_id)
        self.accounts[entity_id].grant(amount)

    def deny(self, entity_id: str) -> None:
        """Record a resource denial to an entity."""
        if entity_id not in self.accounts:
            self.register(entity_id)
        self.accounts[entity_id].deny()

    def consume(self, entity_id: str, amount: float) -> None:
        """Record resource consumption by an entity."""
        if entity_id not in self.accounts:
            self.register(entity_id)
        self.accounts[entity_id].consume(amount)

    def check_compassion(self) -> CompassionState:
        """
        Evaluate compassion state across all accounts.
        Updates starvation scores and determines if redistribution is needed.
        """
        if not self.flags.compassion_layer:
            self.state = CompassionState.DORMANT
            return self.state

        # Update all starvation scores
        for account in self.accounts.values():
            account.update_starvation()

        # Find the most starved entity
        max_starvation = max(
            (a.starvation_score for a in self.accounts.values()),
            default=0.0
        )

        if max_starvation >= self.critical_threshold:
            self.state = CompassionState.CRITICAL
        elif max_starvation >= self.starvation_threshold:
            self.state = CompassionState.ACTIVE
        elif max_starvation >= self.monitoring_threshold:
            self.state = CompassionState.MONITORING
        else:
            self.state = CompassionState.DORMANT

        return self.state

    def redistribute(self) -> dict:
        """
        Redistribute resources from surplus entities to starving entities.
        Returns a record of what was redistributed.

        Compassion is not charity. It's a survival mechanism.
        A system that lets parts starve becomes brittle.
        """
        if self.state not in (CompassionState.ACTIVE, CompassionState.CRITICAL):
            return {"action": "none", "reason": "no starvation detected"}

        # Identify starving and surplus entities
        starving = [(eid, acc) for eid, acc in self.accounts.items()
                    if acc.starvation_score >= self.monitoring_threshold]
        surplus = [(eid, acc) for eid, acc in self.accounts.items()
                   if acc.starvation_score < self.monitoring_threshold
                   and acc.allocated - acc.consumed > 0]

        if not starving or not surplus:
            return {"action": "none", "reason": "no surplus available"}

        # Sort by need (most starved first) and surplus (most surplus first)
        starving.sort(key=lambda x: x[1].starvation_score, reverse=True)
        surplus.sort(key=lambda x: x[1].allocated - x[1].consumed, reverse=True)

        redistributions = []
        total_moved = 0.0

        for s_eid, s_acc in starving:
            needed = (1.0 - s_acc.starvation_score) * 10.0  # target allocation
            for su_eid, su_acc in surplus:
                available = su_acc.allocated - su_acc.consumed
                if available <= 0:
                    continue
                move_amount = min(needed, available * 0.3)  # take max 30% of surplus
                if move_amount <= 0:
                    continue

                # Execute redistribution
                su_acc.allocated -= move_amount
                s_acc.grant(move_amount)
                total_moved += move_amount
                needed -= move_amount

                redistributions.append({
                    "from": su_eid,
                    "to": s_eid,
                    "amount": round(move_amount, 4),
                    "starvation_before": round(s_acc.starvation_score, 4),
                })

                if needed <= 0:
                    break

        result = {
            "action": "redistribute",
            "state": self.state.value,
            "count": len(redistributions),
            "total_moved": round(total_moved, 4),
            "redistributions": redistributions,
            "timestamp": time.time(),
        }
        self.redistribution_log.append(result)
        self.total_redistributions += 1
        return result

    def status(self) -> dict:
        """Full status report."""
        return {
            "flags": self.flags.to_dict(),
            "compassion_state": self.state.value,
            "total_redistributions": self.total_redistributions,
            "accounts": {
                eid: {
                    "allocated": round(acc.allocated, 2),
                    "consumed": round(acc.consumed, 2),
                    "denied": acc.denied_count,
                    "granted": acc.granted_count,
                    "starvation": round(acc.starvation_score, 4),
                }
                for eid, acc in self.accounts.items()
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("═" * 70)
    print("EVEZ-OS MORAL REGISTRY — Self Test")
    print("═" * 70)

    registry = MoralRegistry()
    registry.register("OP_ALPHA")
    registry.register("OP_BETA")
    registry.register("OP_GAMMA")
    registry.register("OP_DELTA")

    # Simulate unfair allocation — ALPHA gets everything, DELTA starves
    print("\n[TEST] Simulating unfair allocation (ALPHA surplus, DELTA starving)...")
    for _ in range(10):
        registry.grant("OP_ALPHA", 5.0)
        registry.grant("OP_BETA", 3.0)
        registry.grant("OP_GAMMA", 1.0)
        registry.deny("OP_DELTA")

    state = registry.check_compassion()
    print(f"  Compassion state: {state.value}")
    print(f"  DELTA starvation: {registry.accounts['OP_DELTA'].starvation_score:.4f}")
    print(f"  ALPHA surplus: {registry.accounts['OP_ALPHA'].allocated - registry.accounts['OP_ALPHA'].consumed:.2f}")

    if state in (CompassionState.ACTIVE, CompassionState.CRITICAL):
        print("\n[TEST] Triggering redistribution...")
        result = registry.redistribute()
        print(f"  Action: {result['action']}")
        print(f"  Redistributions: {result['count']}")
        print(f"  Total moved: {result['total_moved']}")
        for r in result['redistributions']:
            print(f"    {r['from']} → {r['to']}: {r['amount']}")

    print(f"\n[STATUS] Full registry status:")
    print(json.dumps(registry.status(), indent=2))

    print("\n✓ Moral Registry operational")
