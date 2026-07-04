#!/usr/bin/env python3
"""
evez_gnw.py — Global Neuronal Workspace
=======================================
The broadcast/binding layer. All operator outputs converge here.
GNW integrates them into a unified cognitive state and broadcasts back.

Global Workspace Theory: consciousness emerges when information is broadcast
across specialized modules. GNW IS that broadcast mechanism.

This is not a stub. It reads real operator outputs from the spine,
integrates them into a unified state vector, and broadcasts back.
"""

import asyncio
import json
import time
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum

# Import from production core
from evez_os_core import Spine, Event, shannon_entropy, hash_sig, now_iso


class BindingState(Enum):
    UNBOUND = "unbound"
    COMPETING = "competing"
    BOUND = "bound"
    CONFLICTED = "conflicted"


@dataclass
class WorkspaceState:
    """The unified cognitive state — what the system 'knows' right now."""
    timestamp: float = field(default_factory=time.time)
    active_domains: list = field(default_factory=list)
    dominant_operator: str = ""
    phi: float = 0.0
    theta: float = 0.0
    tau: float = 0.0
    poly_c: float = 0.0
    binding_state: BindingState = BindingState.UNBOUND
    competition_winner: dict = field(default_factory=dict)
    integrated_signal: dict = field(default_factory=dict)
    broadcast_hash: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["binding_state"] = self.binding_state.value
        return d


class GNW:
    """
    Global Neuronal Workspace.

    Receives broadcasts from all operators via spine subscription.
    Integrates them through competition (highest-entropy signal wins).
    Broadcasts unified state back to all operators via content bus.

    The competition is real: when multiple operators produce output
    in the same cycle, the one with the highest entropy wins dominance.
    This is not arbitrary — it mirrors neuronal competition in biological
    global workspace models.
    """

    def __init__(self, spine: Spine, content_bus: 'ContentBus' = None):
        self.spine = spine
        self.content_bus = content_bus
        self.state = WorkspaceState()
        self.history: list[dict] = []
        self.cycle_signals: dict[str, dict] = {}  # operator → latest output

        # Subscribe to all operator broadcasts
        for event_type in ["oracle_pulse", "cross_domain", "theta_shift",
                           "grant_collapse", "compassion", "fire_event"]:
            spine.subscribe(event_type, self._on_signal)

    async def _on_signal(self, event: Event):
        """Receive operator signal. Store for next integration cycle."""
        source = event.agent_source or event.type
        self.cycle_signals[source] = {
            "type": event.type,
            "payload": event.payload,
            "timestamp": event.timestamp,
            "entropy": event.payload.get("entropy_bits", 0),
            "hash": event.hash,
        }

    async def integrate(self) -> WorkspaceState:
        """
        Integrate all received signals into unified workspace state.
        Competition: highest-entropy signal wins dominance.
        Binding: if signals agree on domain, bind. If conflict, mark conflicted.
        """
        if not self.cycle_signals:
            self.state.binding_state = BindingState.UNBOUND
            return self.state

        # Competition phase: find dominant signal
        ranked = sorted(self.cycle_signals.items(),
                        key=lambda x: x[1].get("entropy", 0), reverse=True)
        winner_source, winner_signal = ranked[0]

        # Collect active domains
        domains = set()
        for sig in self.cycle_signals.values():
            d = sig["payload"].get("domain", "")
            if d:
                domains.add(d)
            ds = sig["payload"].get("domains", [])
            domains.update(ds)

        # Check for binding (agreement) or conflict
        entropies = [s.get("entropy", 0) for s in self.cycle_signals.values()]
        entropy_spread = max(entropies) - min(entropies) if entropies else 0

        if entropy_spread > 1.5 and len(self.cycle_signals) > 1:
            self.state.binding_state = BindingState.CONFLICTED
        elif len(domains) == 1:
            self.state.binding_state = BindingState.BOUND
        else:
            self.state.binding_state = BindingState.COMPETING

        # Build integrated state
        self.state = WorkspaceState(
            timestamp=time.time(),
            active_domains=sorted(domains),
            dominant_operator=winner_source,
            phi=self.spine.density * 5.0,
            theta=winner_signal["payload"].get("theta_shift", 0),
            tau=winner_signal["payload"].get("tau", winner_signal.get("entropy", 0) * 4.5),
            poly_c=self.spine.density,
            binding_state=self.state.binding_state,
            competition_winner={
                "source": winner_source,
                "entropy": winner_signal.get("entropy", 0),
                "type": winner_signal["type"],
            },
            integrated_signal={
                "total_signals": len(self.cycle_signals),
                "entropy_spread": round(entropy_spread, 4),
                "domains_active": len(domains),
                "all_sources": list(self.cycle_signals.keys()),
            },
            broadcast_hash=hash_sig(f"{time.time()}:{json.dumps(sorted(domains))}"),
        )

        # Record history
        self.history.append(self.state.to_dict())

        # Broadcast to content bus
        if self.content_bus:
            await self.content_bus.write("gnw_state", self.state.to_dict())

        # Clear cycle signals for next round
        self.cycle_signals.clear()

        return self.state

    def stats(self) -> dict:
        return {
            "total_integrations": len(self.history),
            "current_state": self.state.binding_state.value,
            "active_domains": self.state.active_domains,
            "dominant_operator": self.state.dominant_operator,
            "phi": round(self.state.phi, 4),
            "poly_c": round(self.state.poly_c, 4),
        }
