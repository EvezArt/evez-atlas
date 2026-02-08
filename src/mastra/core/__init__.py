"""
HandshakeOS-E Core Module

This module contains the foundational data structures for the HandshakeOS-E system:
- UniversalEventRecord: Domain-agnostic event recording with state tracking
- IntentToken: Pre/post-action intent tracking with audit trails
- ParallelHypotheses: Multi-perspective hypothesis testing (me/we/they/system)
- TestObject: First-class test objects linked to hypotheses
- BoundedIdentity: Agent identity and permission management
- AuditLogger: Centralized audit logging
- ReversibilityManager: Action reversal system

Design Principles:
1. No single-domain bias - all events have emergent domain mixture vectors
2. Complete attributability - every action traces to a bounded identity
3. Full auditability - comprehensive audit trails for all operations
4. Reversibility by design - actions marked as reversible with undo procedures
5. Multi-perspective testing - hypotheses evaluated from me/we/they/system views
6. First-class tests - tests are objects linked to hypotheses
7. Write for the stranger - documentation for future maintainers

For the stranger who wears your shell tomorrow:
- Read HANDSHAKEOS_E_ARTIFACT_INVENTORY.md for complete system overview
- Each class has comprehensive docstrings with usage examples
- Tests demonstrate integration patterns
- Demo scripts show features in action
"""

from .universal_event_record import UniversalEventRecord, DomainSignature
from .intent_token import IntentToken, PreAction, PostAction
from .parallel_hypotheses import ParallelHypotheses, HypothesisPerspective
from .test_object import TestObject, TestResult
from .bounded_identity import BoundedIdentity, PermissionScope
from .audit_logger import AuditLogger
from .reversibility import ReversibilityManager

__all__ = [
    'UniversalEventRecord',
    'DomainSignature',
    'IntentToken',
    'PreAction',
    'PostAction',
    'ParallelHypotheses',
    'HypothesisPerspective',
    'TestObject',
    'TestResult',
    'BoundedIdentity',
    'PermissionScope',
    'AuditLogger',
    'ReversibilityManager',
]

__version__ = '1.0.0'
