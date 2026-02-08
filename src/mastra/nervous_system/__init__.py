"""
HandshakeOS-E Nervous System Infrastructure

A domain-agnostic event recording and hypothesis tracking system that makes
every handshake knowable, forces truth-telling, enables rapid fix/verify cycles,
prevents organizational fragmentation, and makes rollback and attribution easy and safe.

Core components:
- UniversalEvent: domain-agnostic event records with mixture vectors
- IntentToken: pre-action intent declaration
- EventReadout: post-event analysis and payoff
- Hypothesis: parallel model tracking (me/we/they/system)
- Test: first-class test objects linked to hypotheses
- Actor: identity for attribution

All interventions are:
- Auditable: full event log with attribution
- Attributable: every action linked to an actor
- Reversible: versioned with rollback support
"""

from .core import (
    UniversalEvent,
    IntentToken,
    EventReadout,
    Hypothesis,
    Test,
    Actor,
    MixtureVector,
    NervousSystem,
    ModelType,
)

__all__ = [
    "UniversalEvent",
    "IntentToken",
    "EventReadout",
    "Hypothesis",
    "Test",
    "Actor",
    "MixtureVector",
    "NervousSystem",
    "ModelType",
]
