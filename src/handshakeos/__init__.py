"""
HandshakeOS-E Nervous System

A universal event-driven architecture for tracking internal state, routing,
negotiation, social dynamics, and model-to-user interaction without requiring
any single domain as primary.

Core Components:
- UniversalEventRecord: Domain-agnostic event tracking
- IntentToken: Pre-action and post-event causal tracking
- Hypothesis: Parallel model tracking (me/we/they/system)
- Test: First-class test objects linked to hypotheses
"""

from .event_record import UniversalEventRecord, DomainMixtureVector, EventSource
from .intent_token import IntentToken, PreActionIntent, PostEventCausal, IntentStatus
from .hypothesis import Hypothesis, ParallelModel, Falsifier, ModelPerspective
from .test_object import TestObject, TestResult, TestType, TestStatus

__all__ = [
    "UniversalEventRecord",
    "DomainMixtureVector",
    "EventSource",
    "IntentToken",
    "PreActionIntent",
    "PostEventCausal",
    "IntentStatus",
    "Hypothesis",
    "ParallelModel",
    "Falsifier",
    "ModelPerspective",
    "TestObject",
    "TestResult",
    "TestType",
    "TestStatus",
]

__version__ = "0.1.0"
