"""
Tests for HandshakeOS-E Core Components

Comprehensive test suite for:
- UniversalEventRecord
- IntentToken
- ParallelHypotheses
- TestObject
- BoundedIdentity
- AuditLogger
- ReversibilityManager
"""

import pytest
import tempfile
import os
import json
from datetime import datetime
from pathlib import Path

# Import all core components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mastra.core import (
    UniversalEventRecord, DomainSignature, create_event,
    IntentToken, PreAction, PostAction,
    ParallelHypotheses, HypothesisPerspective,
    TestObject, TestResult,
    BoundedIdentity, PermissionScope,
    AuditLogger,
    ReversibilityManager
)


class TestUniversalEventRecord:
    """Test UniversalEventRecord functionality."""
    
    def test_create_event(self):
        """Test basic event creation."""
        event = create_event(
            event_type="test_event",
            attributed_to="test_agent",
            state_before={"value": 1},
            state_after={"value": 2}
        )
        
        assert event.event_type == "test_event"
        assert event.attributed_to == "test_agent"
        assert event.state_before["value"] == 1
        assert event.state_after["value"] == 2
    
    def test_state_delta_computation(self):
        """Test automatic state delta computation."""
        event = UniversalEventRecord(
            event_type="update",
            attributed_to="agent",
            state_before={"a": 1, "b": 2, "c": 3},
            state_after={"a": 1, "b": 5, "d": 4}
        )
        
        # Check delta
        assert "b" in event.state_delta["changed"]
        assert event.state_delta["changed"]["b"]["from"] == 2
        assert event.state_delta["changed"]["b"]["to"] == 5
        assert "d" in event.state_delta["added"]
        assert "c" in event.state_delta["removed"]
    
    def test_domain_entropy(self):
        """Test domain signature entropy calculation."""
        sig = DomainSignature(
            technical=0.5,
            social=0.3,
            cognitive=0.2
        )
        
        entropy = sig.calculate_entropy()
        assert entropy > 0  # Mixed domains should have positive entropy
        
        # Single domain should have zero entropy
        sig_single = DomainSignature(technical=1.0)
        assert sig_single.calculate_entropy() == 0.0
    
    def test_audit_log(self):
        """Test audit log functionality."""
        event = create_event("test", "agent")
        event.add_audit_entry("created", "agent", {"source": "test"})
        
        assert len(event.audit_log) == 1
        assert event.audit_log[0]["action"] == "created"
        assert event.audit_log[0]["actor"] == "agent"
    
    def test_save_load_jsonl(self):
        """Test JSONL persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "events", "test.jsonl")
            
            event = create_event("test", "agent", state_before={}, state_after={"x": 1})
            event.save_to_log(log_path)
            
            loaded = UniversalEventRecord.load_from_log(log_path)
            assert len(loaded) == 1
            assert loaded[0].event_type == "test"
            assert loaded[0].attributed_to == "agent"


class TestIntentToken:
    """Test IntentToken functionality."""
    
    def test_create_intent(self):
        """Test intent creation with pre-action."""
        intent = IntentToken(
            pre_action=PreAction(
                goal="Test goal",
                confidence=0.8,
                constraints=["Must be fast"],
                success_criteria=["Result obtained"]
            ),
            attributed_to="agent"
        )
        
        assert intent.pre_action.goal == "Test goal"
        assert intent.pre_action.confidence == 0.8
        assert not intent.is_complete()
    
    def test_complete_intent(self):
        """Test completing an intent."""
        intent = IntentToken(
            pre_action=PreAction(goal="Test", confidence=0.7),
            attributed_to="agent"
        )
        
        intent.complete(
            trigger="user_request",
            final_state={"result": "success"},
            payoff=0.9
        )
        
        assert intent.is_complete()
        assert intent.post_action.payoff == 0.9
        assert intent.post_action.trigger == "user_request"
    
    def test_measurements(self):
        """Test measurement tracking."""
        intent = IntentToken(pre_action=PreAction(), attributed_to="agent")
        
        intent.add_measurement("latency_ms", 42, "milliseconds")
        intent.add_measurement("success", True, "boolean")
        
        assert len(intent.measurements) == 2
        assert intent.measurements[0]["metric"] == "latency_ms"
        assert intent.measurements[0]["value"] == 42
    
    def test_confidence_gap(self):
        """Test confidence vs outcome gap calculation."""
        intent = IntentToken(
            pre_action=PreAction(confidence=0.9),
            attributed_to="agent"
        )
        intent.complete("trigger", {}, payoff=0.5)
        
        gap = intent.confidence_vs_outcome_gap()
        assert gap == 0.4  # |0.9 - 0.5|


class TestParallelHypotheses:
    """Test ParallelHypotheses functionality."""
    
    def test_create_hypotheses(self):
        """Test hypothesis creation."""
        hyp = ParallelHypotheses(
            context="Test context",
            me_perspective=HypothesisPerspective(
                hypothesis="Test hypothesis",
                probability=0.7,
                proposed_by="agent"
            )
        )
        
        assert hyp.context == "Test context"
        assert hyp.me_perspective.probability == 0.7
    
    def test_consensus_calculation(self):
        """Test consensus probability calculation."""
        hyp = ParallelHypotheses(
            context="Test",
            me_perspective=HypothesisPerspective(probability=0.8),
            we_perspective=HypothesisPerspective(probability=0.7),
            they_perspective=HypothesisPerspective(probability=0.6),
            system_perspective=HypothesisPerspective(probability=0.5)
        )
        
        consensus = hyp.calculate_consensus()
        assert consensus == 0.65  # (0.8 + 0.7 + 0.6 + 0.5) / 4
    
    def test_divergence_calculation(self):
        """Test divergence score calculation."""
        hyp = ParallelHypotheses(
            context="Test",
            me_perspective=HypothesisPerspective(probability=0.5),
            we_perspective=HypothesisPerspective(probability=0.5),
            they_perspective=HypothesisPerspective(probability=0.5),
            system_perspective=HypothesisPerspective(probability=0.5)
        )
        
        divergence = hyp.calculate_divergence()
        assert divergence == 0.0  # All same = no divergence
    
    def test_evidence_tracking(self):
        """Test evidence addition and tracking."""
        hyp = ParallelHypotheses(context="Test")
        
        hyp.update_with_evidence(
            "event_001",
            supports_perspectives=["me", "we"],
            contradicts_perspectives=["they"]
        )
        
        assert len(hyp.me_perspective.supporting_evidence) == 1
        assert len(hyp.they_perspective.contradicting_evidence) == 1
    
    def test_strongest_weakest(self):
        """Test finding strongest and weakest perspectives."""
        hyp = ParallelHypotheses(
            context="Test",
            me_perspective=HypothesisPerspective(probability=0.9),
            we_perspective=HypothesisPerspective(probability=0.3),
            they_perspective=HypothesisPerspective(probability=0.6),
            system_perspective=HypothesisPerspective(probability=0.5)
        )
        
        strongest = hyp.get_strongest_perspective()
        weakest = hyp.get_weakest_perspective()
        
        assert strongest.probability == 0.9
        assert weakest.probability == 0.3


class TestTestObject:
    """Test TestObject functionality."""
    
    def test_create_test(self):
        """Test test object creation."""
        test = TestObject(
            test_name="Test API",
            test_type="integration",
            hypothesis_ids=["hyp_001"],
            created_by="agent"
        )
        
        assert test.test_name == "Test API"
        assert test.test_type == "integration"
        assert len(test.hypothesis_ids) == 1
    
    def test_record_result(self):
        """Test recording test results."""
        test = TestObject(test_name="Test", created_by="agent")
        
        result = TestResult(
            passed=True,
            execution_time_ms=42.5,
            output="Success"
        )
        test.record_result(result)
        
        assert len(test.execution_history) == 1
        assert test.last_result.passed
        assert test.last_result.execution_time_ms == 42.5
    
    def test_pass_rate_calculation(self):
        """Test pass rate calculation."""
        test = TestObject(test_name="Test", created_by="agent")
        
        # Add results: 3 pass, 1 fail
        for passed in [True, True, True, False]:
            test.record_result(TestResult(passed=passed))
        
        assert test.calculate_pass_rate() == 0.75
    
    def test_flakiness_detection(self):
        """Test flakiness detection."""
        test = TestObject(test_name="Test", created_by="agent")
        
        # Stable test
        for _ in range(10):
            test.record_result(TestResult(passed=True))
        assert not test.is_flaky()
        
        # Add a failure (now 90% pass rate, below 95% threshold)
        test.record_result(TestResult(passed=False))
        assert test.is_flaky()


class TestBoundedIdentity:
    """Test BoundedIdentity functionality."""
    
    def test_create_identity(self):
        """Test identity creation."""
        identity = BoundedIdentity(
            entity_name="test_agent",
            entity_type="agent",
            tier_level=2
        )
        
        assert identity.entity_name == "test_agent"
        assert identity.tier_level == 2
        assert not identity.verified
    
    def test_permission_checking(self):
        """Test permission checking."""
        identity = BoundedIdentity(
            entity_name="agent",
            tier_level=2,
            permission_scope=PermissionScope(
                read=True,
                write=True,
                execute=False
            )
        )
        
        assert identity.has_permission("read")
        assert identity.has_permission("write")
        assert not identity.has_permission("execute")
    
    def test_permission_granting(self):
        """Test granting permissions."""
        identity = BoundedIdentity(entity_name="agent")
        
        identity.grant_permission("admin", "superuser")
        assert identity.has_permission("admin")
    
    def test_verification(self):
        """Test identity verification."""
        identity = BoundedIdentity(entity_name="agent")
        
        identity.verify_identity("signature", "verified_by_admin")
        assert identity.verified
        assert identity.verification_method == "signature"


class TestAuditLogger:
    """Test AuditLogger functionality."""
    
    def test_singleton(self):
        """Test singleton pattern."""
        logger1 = AuditLogger()
        logger2 = AuditLogger()
        assert logger1 is logger2
    
    def test_log_action(self):
        """Test action logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            logger.log_action(
                action="test_action",
                entity_id="agent_001",
                details={"key": "value"}
            )
            
            # Check log was written
            log_path = os.path.join(tmpdir, "audit.jsonl")
            assert os.path.exists(log_path)
    
    def test_query_logs(self):
        """Test log querying."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            # Log multiple actions
            logger.log_action("action1", "agent_001", {})
            logger.log_action("action2", "agent_002", {})
            logger.log_action("action1", "agent_001", {})
            
            # Query by entity
            results = logger.query_logs(filters={"entity_id": "agent_001"})
            assert len(results) == 2
    
    def test_integrity_verification(self):
        """Test log integrity verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            
            logger.log_action("action", "agent", {})
            
            # Should pass integrity check
            assert logger.verify_log_integrity()


class TestReversibilityManager:
    """Test ReversibilityManager functionality."""
    
    def test_mark_reversible(self):
        """Test marking actions as reversible."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReversibilityManager(storage_dir=tmpdir)
            
            def undo_fn():
                return {"status": "undone"}
            
            manager.mark_reversible(
                "action_001",
                undo_procedure=undo_fn,
                context={"key": "value"}
            )
            
            assert manager.is_reversible("action_001")
    
    def test_reverse_action(self):
        """Test action reversal."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReversibilityManager(storage_dir=tmpdir)
            
            # Create a simple undo function
            state = {"value": 1}
            def undo_fn():
                state["value"] = 0
                return True
            
            manager.mark_reversible("action_001", undo_procedure=undo_fn)
            
            # Reverse it
            result = manager.reverse_action("action_001", "admin")
            assert result is True
            assert state["value"] == 0
    
    def test_idempotent_reversal(self):
        """Test that actions can only be reversed once."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReversibilityManager(storage_dir=tmpdir)
            
            def undo_fn():
                return True
            
            manager.mark_reversible("action_001", undo_procedure=undo_fn)
            
            # First reversal succeeds
            assert manager.reverse_action("action_001", "admin") is True
            
            # Second reversal fails (already reversed)
            assert manager.reverse_action("action_001", "admin") is False
    
    def test_dependent_actions(self):
        """Test dependent action tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ReversibilityManager(storage_dir=tmpdir)
            
            manager.mark_reversible("action_001", undo_procedure=lambda: True)
            manager.mark_reversible(
                "action_002",
                undo_procedure=lambda: True,
                depends_on=["action_001"]
            )
            
            # Cannot reverse action_001 without first reversing action_002
            result = manager.reverse_action("action_001", "admin")
            assert result is False  # Has dependents


class TestIntegration:
    """Test integration between components."""
    
    def test_event_intent_link(self):
        """Test linking events and intents."""
        event = create_event("test", "agent")
        intent = IntentToken(pre_action=PreAction(goal="Test"), attributed_to="agent")
        
        # Link them
        intent.link_event(event.event_id)
        
        assert event.event_id in intent.related_events
    
    def test_hypothesis_test_link(self):
        """Test linking hypotheses and tests."""
        hyp = ParallelHypotheses(context="Test")
        test = TestObject(
            test_name="Test hypothesis",
            hypothesis_ids=[hyp.hypothesis_id],
            created_by="agent"
        )
        
        # Link test to hypothesis
        hyp.me_perspective.link_test(test.test_id)
        
        assert test.test_id in hyp.me_perspective.test_ids
    
    def test_full_workflow(self):
        """Test complete workflow: event -> intent -> hypothesis -> test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create event
            event = create_event(
                "user_query",
                "agent_001",
                state_before={"query": None},
                state_after={"query": "What is X?"}
            )
            event.save_to_log(os.path.join(tmpdir, "events.jsonl"))
            
            # Create intent
            intent = IntentToken(
                pre_action=PreAction(
                    goal="Answer user query",
                    confidence=0.8
                ),
                attributed_to="agent_001"
            )
            intent.link_event(event.event_id)
            intent.complete("user_request", {"answer": "X is..."}, payoff=0.9)
            intent.save_to_log(os.path.join(tmpdir, "intents.jsonl"))
            
            # Create hypothesis
            hyp = ParallelHypotheses(
                context="User satisfaction with answer",
                me_perspective=HypothesisPerspective(
                    hypothesis="User is satisfied",
                    probability=0.85,
                    proposed_by="agent_001"
                )
            )
            hyp.link_event(event.event_id)
            hyp.link_intent(intent.token_id)
            hyp.save_to_log(os.path.join(tmpdir, "hypotheses.jsonl"))
            
            # Create test
            test = TestObject(
                test_name="Verify user satisfaction",
                test_description="Check if user gave positive feedback",
                hypothesis_ids=[hyp.hypothesis_id],
                perspective_filter=["me"],
                created_by="agent_001"
            )
            test.save_to_log(os.path.join(tmpdir, "tests.jsonl"))
            
            # Verify all files exist
            assert os.path.exists(os.path.join(tmpdir, "events.jsonl"))
            assert os.path.exists(os.path.join(tmpdir, "intents.jsonl"))
            assert os.path.exists(os.path.join(tmpdir, "hypotheses.jsonl"))
            assert os.path.exists(os.path.join(tmpdir, "tests.jsonl"))
            
            # Load and verify
            events = UniversalEventRecord.load_from_log(os.path.join(tmpdir, "events.jsonl"))
            intents = IntentToken.load_from_log(os.path.join(tmpdir, "intents.jsonl"))
            hypotheses = ParallelHypotheses.load_from_log(os.path.join(tmpdir, "hypotheses.jsonl"))
            tests = TestObject.load_from_log(os.path.join(tmpdir, "tests.jsonl"))
            
            assert len(events) == 1
            assert len(intents) == 1
            assert len(hypotheses) == 1
            assert len(tests) == 1
            
            # Verify linkage
            assert event.event_id in intents[0].related_events
            assert event.event_id in hypotheses[0].related_events
            assert intent.token_id in hypotheses[0].related_intents


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
