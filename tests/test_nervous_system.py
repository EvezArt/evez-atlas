"""
Test suite for HandshakeOS-E Nervous System.

Tests cover:
- Event recording and querying
- Intent and readout tracking
- Hypothesis management
- Test linkage
- Attribution and auditability
- Rollback via versioning
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.mastra.nervous_system import (
    NervousSystem,
    Actor,
    IntentToken,
    EventReadout,
    MixtureVector,
    Hypothesis,
    Test,
    ModelType,
)


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def nervous_system(temp_data_dir):
    """Create nervous system instance for testing."""
    return NervousSystem(temp_data_dir)


@pytest.fixture
def test_actor(nervous_system):
    """Create test actor."""
    actor = Actor(
        name="Test Actor",
        type="test",
        permissions={"record_events", "create_hypotheses", "create_tests"}
    )
    return nervous_system.register_actor(actor)


class TestActorManagement:
    """Test actor registration and retrieval."""
    
    def test_register_actor(self, nervous_system):
        """Test actor registration."""
        actor = Actor(name="Agent A", type="agent")
        registered = nervous_system.register_actor(actor)
        
        assert registered.id == actor.id
        assert registered.name == "Agent A"
        assert registered.type == "agent"
    
    def test_get_actor(self, nervous_system):
        """Test actor retrieval."""
        actor = Actor(name="Agent B", type="agent")
        nervous_system.register_actor(actor)
        
        retrieved = nervous_system.get_actor(actor.id)
        assert retrieved is not None
        assert retrieved.id == actor.id
        assert retrieved.name == "Agent B"
    
    def test_actor_persistence(self, temp_data_dir):
        """Test actor persistence across instances."""
        # Create and register actor
        ns1 = NervousSystem(temp_data_dir)
        actor = Actor(name="Persistent Actor", type="agent")
        ns1.register_actor(actor)
        
        # Create new instance and verify actor is loaded
        ns2 = NervousSystem(temp_data_dir)
        retrieved = ns2.get_actor(actor.id)
        assert retrieved is not None
        assert retrieved.name == "Persistent Actor"


class TestEventRecording:
    """Test event recording and management."""
    
    def test_record_basic_event(self, nervous_system, test_actor):
        """Test basic event recording."""
        event = nervous_system.record_event(
            actor_id=test_actor.id,
            metadata={"test": "basic"}
        )
        
        assert event.id is not None
        assert event.actor_id == test_actor.id
        assert event.metadata["test"] == "basic"
        assert event.version == 1
    
    def test_record_event_with_intent(self, nervous_system, test_actor):
        """Test event recording with intent."""
        intent = IntentToken(
            goal="Test goal",
            constraints=["constraint1", "constraint2"],
            success_metric="Test metric",
            confidence=0.85
        )
        
        event = nervous_system.record_event(
            actor_id=test_actor.id,
            intent=intent
        )
        
        assert event.intent is not None
        assert event.intent.goal == "Test goal"
        assert event.intent.confidence == 0.85
        assert len(event.intent.constraints) == 2
    
    def test_update_event_with_readout(self, nervous_system, test_actor):
        """Test updating event with readout."""
        event = nervous_system.record_event(actor_id=test_actor.id)
        
        readout = EventReadout(
            trigger="test_trigger",
            result_state={"key": "value"},
            policy_used="test_policy",
            payoff=1.5,
            success=True
        )
        
        updated = nervous_system.update_event(event.id, readout=readout)
        
        assert updated.readout is not None
        assert updated.readout.trigger == "test_trigger"
        assert updated.readout.success is True
        assert updated.readout.payoff == 1.5
        assert updated.version == 2  # Version incremented
    
    def test_get_event(self, nervous_system, test_actor):
        """Test event retrieval."""
        event = nervous_system.record_event(actor_id=test_actor.id)
        
        retrieved = nervous_system.get_event(event.id)
        assert retrieved is not None
        assert retrieved.id == event.id
    
    def test_query_events_by_actor(self, nervous_system, test_actor):
        """Test querying events by actor."""
        # Create multiple events
        for i in range(3):
            nervous_system.record_event(
                actor_id=test_actor.id,
                metadata={"index": i}
            )
        
        events = nervous_system.query_events(actor_id=test_actor.id)
        assert len(events) == 3
    
    def test_event_with_mixture_vector(self, nervous_system, test_actor):
        """Test event with mixture vector."""
        mixture = MixtureVector(
            components={"domain1": 0.6, "domain2": 0.4},
            normalized=True
        )
        
        event = nervous_system.record_event(
            actor_id=test_actor.id,
            mixture=mixture
        )
        
        assert event.mixture is not None
        assert "domain1" in event.mixture.components
        assert event.mixture.normalized is True


class TestMixtureVector:
    """Test mixture vector functionality."""
    
    def test_create_mixture_vector(self):
        """Test creating mixture vector."""
        mv = MixtureVector(
            components={"a": 2.0, "b": 3.0},
            normalized=False
        )
        
        assert mv.components["a"] == 2.0
        assert mv.components["b"] == 3.0
        assert mv.normalized is False
    
    def test_normalize_mixture_vector(self):
        """Test normalizing mixture vector."""
        mv = MixtureVector(components={"a": 2.0, "b": 3.0})
        mv.normalize()
        
        assert mv.normalized is True
        assert abs(mv.components["a"] - 0.4) < 0.001
        assert abs(mv.components["b"] - 0.6) < 0.001
        assert abs(sum(mv.components.values()) - 1.0) < 0.001
    
    def test_empty_mixture_vector(self):
        """Test empty mixture vector (unknown domain)."""
        mv = MixtureVector()
        
        assert len(mv.components) == 0
        assert mv.normalized is False


class TestHypothesisManagement:
    """Test hypothesis tracking."""
    
    def test_create_hypothesis(self, nervous_system):
        """Test creating hypothesis."""
        hyp = nervous_system.create_hypothesis(
            model_type=ModelType.ME,
            description="Test hypothesis",
            probability=0.7,
            falsifiers=["condition1", "condition2"]
        )
        
        assert hyp.id is not None
        assert hyp.model_type == ModelType.ME
        assert hyp.description == "Test hypothesis"
        assert hyp.probability == 0.7
        assert len(hyp.falsifiers) == 2
    
    def test_hypothesis_for_each_model_type(self, nervous_system):
        """Test creating hypothesis for each model type."""
        for model_type in ModelType:
            hyp = nervous_system.create_hypothesis(
                model_type=model_type,
                description=f"Hypothesis for {model_type.value}"
            )
            assert hyp.model_type == model_type
    
    def test_update_hypothesis_probability(self, nervous_system):
        """Test updating hypothesis probability."""
        hyp = nervous_system.create_hypothesis(
            model_type=ModelType.SYSTEM,
            description="Test",
            probability=0.5
        )
        
        updated = nervous_system.update_hypothesis(
            hyp.id,
            probability=0.8
        )
        
        assert updated.probability == 0.8
        assert updated.version == 2
    
    def test_add_evidence_to_hypothesis(self, nervous_system, test_actor):
        """Test adding evidence to hypothesis."""
        hyp = nervous_system.create_hypothesis(
            model_type=ModelType.ME,
            description="Test"
        )
        
        event = nervous_system.record_event(actor_id=test_actor.id)
        
        updated = nervous_system.update_hypothesis(
            hyp.id,
            add_evidence=event.id
        )
        
        assert event.id in updated.evidence
    
    def test_get_hypotheses_by_model(self, nervous_system):
        """Test getting hypotheses by model type."""
        # Create ME hypotheses
        for i in range(2):
            nervous_system.create_hypothesis(
                model_type=ModelType.ME,
                description=f"ME hypothesis {i}"
            )
        
        # Create WE hypotheses
        for i in range(3):
            nervous_system.create_hypothesis(
                model_type=ModelType.WE,
                description=f"WE hypothesis {i}"
            )
        
        me_hyps = nervous_system.get_hypotheses_by_model(ModelType.ME)
        we_hyps = nervous_system.get_hypotheses_by_model(ModelType.WE)
        
        assert len(me_hyps) == 2
        assert len(we_hyps) == 3


class TestTestManagement:
    """Test test object management."""
    
    def test_create_test(self, nervous_system):
        """Test creating test linked to hypothesis."""
        hyp = nervous_system.create_hypothesis(
            model_type=ModelType.ME,
            description="Test hypothesis"
        )
        
        test = nervous_system.create_test(
            name="Test validation",
            hypothesis_id=hyp.id,
            test_code="def test(): pass"
        )
        
        assert test.id is not None
        assert test.name == "Test validation"
        assert test.hypothesis_id == hyp.id
    
    def test_record_test_result(self, nervous_system):
        """Test recording test execution result."""
        hyp = nervous_system.create_hypothesis(
            model_type=ModelType.ME,
            description="Test"
        )
        
        test = nervous_system.create_test(
            name="Test",
            hypothesis_id=hyp.id
        )
        
        updated = nervous_system.record_test_result(
            test_id=test.id,
            passed=True,
            result={"metric": 42}
        )
        
        assert updated.passed is True
        assert updated.result["metric"] == 42
        assert updated.executed_at is not None
    
    def test_get_tests_for_hypothesis(self, nervous_system):
        """Test getting all tests for a hypothesis."""
        hyp = nervous_system.create_hypothesis(
            model_type=ModelType.SYSTEM,
            description="Test"
        )
        
        # Create multiple tests
        for i in range(3):
            nervous_system.create_test(
                name=f"Test {i}",
                hypothesis_id=hyp.id
            )
        
        tests = nervous_system.get_tests_for_hypothesis(hyp.id)
        assert len(tests) == 3
    
    def test_test_hypothesis_linkage(self, nervous_system):
        """Test bidirectional test-hypothesis linkage."""
        hyp = nervous_system.create_hypothesis(
            model_type=ModelType.ME,
            description="Test"
        )
        
        test = nervous_system.create_test(
            name="Test",
            hypothesis_id=hyp.id
        )
        
        # Check test links to hypothesis
        assert test.hypothesis_id == hyp.id
        
        # Check hypothesis links to test
        retrieved_hyp = nervous_system.get_hypothesis(hyp.id)
        assert test.id in retrieved_hyp.linked_tests


class TestAttributionAndAudit:
    """Test attribution and auditability."""
    
    def test_get_attribution(self, nervous_system, test_actor):
        """Test getting attribution for event."""
        event = nervous_system.record_event(actor_id=test_actor.id)
        
        attribution = nervous_system.get_attribution(event.id)
        
        assert attribution['event_id'] == event.id
        assert attribution['actor']['id'] == test_actor.id
        assert attribution['created_at'] is not None
        assert attribution['version'] == 1
    
    def test_audit_trail_versioning(self, nervous_system, test_actor):
        """Test audit trail tracks all versions."""
        event = nervous_system.record_event(actor_id=test_actor.id)
        
        # Update multiple times
        for i in range(3):
            readout = EventReadout(trigger=f"update_{i}", success=True)
            nervous_system.update_event(event.id, readout=readout)
        
        trail = nervous_system.get_audit_trail(event.id)
        
        # Should have original + 3 updates = 4 versions
        assert len(trail) == 4
        
        # Verify version numbers
        versions = [entry['version'] for entry in trail]
        assert versions == [1, 2, 3, 4]
    
    def test_no_invisible_agents(self, nervous_system):
        """Test that events require registered actors."""
        with pytest.raises(ValueError):
            nervous_system.record_event(
                actor_id="non-existent-actor"
            )


class TestPersistence:
    """Test data persistence."""
    
    def test_event_persistence(self, temp_data_dir):
        """Test events persist across instances."""
        # Create and record event
        ns1 = NervousSystem(temp_data_dir)
        actor = Actor(name="Test", type="test")
        ns1.register_actor(actor)
        
        event = ns1.record_event(
            actor_id=actor.id,
            metadata={"persisted": True}
        )
        
        # Create new instance and verify event exists
        ns2 = NervousSystem(temp_data_dir)
        retrieved = ns2.get_event(event.id)
        
        assert retrieved is not None
        assert retrieved.metadata["persisted"] is True
    
    def test_hypothesis_persistence(self, temp_data_dir):
        """Test hypotheses persist across instances."""
        ns1 = NervousSystem(temp_data_dir)
        hyp = ns1.create_hypothesis(
            model_type=ModelType.ME,
            description="Persistent hypothesis"
        )
        
        ns2 = NervousSystem(temp_data_dir)
        retrieved = ns2.get_hypothesis(hyp.id)
        
        assert retrieved is not None
        assert retrieved.description == "Persistent hypothesis"


class TestSystemStatistics:
    """Test system statistics and queries."""
    
    def test_get_stats(self, nervous_system, test_actor):
        """Test system statistics."""
        # Create some data
        nervous_system.record_event(actor_id=test_actor.id)
        nervous_system.record_event(actor_id=test_actor.id)
        
        nervous_system.create_hypothesis(
            model_type=ModelType.ME,
            description="Test"
        )
        
        stats = nervous_system.get_stats()
        
        assert stats['total_events'] == 2
        assert stats['total_hypotheses'] == 1
        assert stats['total_actors'] == 1
        assert 'hypotheses_by_model' in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
