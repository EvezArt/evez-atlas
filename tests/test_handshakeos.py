"""
Comprehensive tests for HandshakeOS-E nervous system.

Tests cover:
- Universal event recording
- Intent token lifecycle
- Parallel hypothesis tracking
- Test objects and execution
"""

import pytest
import time
from pathlib import Path
import tempfile
import json

# Import HandshakeOS-E components
from src.handshakeos import (
    UniversalEventRecord,
    EventSource,
    DomainMixtureVector,
    IntentToken,
    PreActionIntent,
    PostEventCausal,
    Hypothesis,
    ModelPerspective,
    ParallelModel,
    Falsifier,
    TestObject,
    TestType,
    TestStatus,
)
from src.handshakeos.event_record import EventLog
from src.handshakeos.intent_token import IntentRegistry, IntentStatus
from src.handshakeos.hypothesis import HypothesisRegistry
from src.handshakeos.test_object import TestRegistry


class TestUniversalEventRecord:
    """Test universal event record functionality"""
    
    def test_create_basic_event(self):
        """Test creating a basic event"""
        event = UniversalEventRecord(
            event_type="test_event",
            payload={"key": "value"},
            source=EventSource.USER_INPUT
        )
        
        assert event.event_id is not None
        assert event.event_type == "test_event"
        assert event.source == EventSource.USER_INPUT
        assert event.payload["key"] == "value"
    
    def test_event_with_empty_domain_mixture(self):
        """Test event with empty domain mixture"""
        mixture = DomainMixtureVector()
        event = UniversalEventRecord(
            event_type="test",
            domain_mixture=mixture
        )
        
        assert event.domain_mixture.is_empty()
    
    def test_event_with_domain_mixture(self):
        """Test event with specified domain mixture"""
        mixture = DomainMixtureVector(
            social_dynamics=0.6,
            model_interaction=0.4,
            confidence=0.8
        )
        event = UniversalEventRecord(
            event_type="interaction",
            domain_mixture=mixture
        )
        
        assert not event.domain_mixture.is_empty()
        assert event.domain_mixture.social_dynamics == 0.6
        assert event.domain_mixture.confidence == 0.8
    
    def test_event_refinement(self):
        """Test refining event domain mixture"""
        event = UniversalEventRecord(event_type="initial")
        
        # Initially no domain mixture
        assert event.domain_mixture is None
        
        # Refine with new mixture
        new_mixture = DomainMixtureVector(
            internal_state=0.7,
            confidence=0.6
        )
        refined = event.refine_domain_mixture(new_mixture)
        
        assert refined.version == 2
        assert refined.supersedes == event.event_id
        assert refined.domain_mixture.internal_state == 0.7
    
    def test_event_serialization(self):
        """Test event to/from dict"""
        event = UniversalEventRecord(
            event_type="serialization_test",
            payload={"data": 123},
            source=EventSource.DEVICE_LOG
        )
        
        # To dict
        data = event.to_dict()
        assert data['event_type'] == "serialization_test"
        assert data['source'] == "device_log"
        
        # From dict
        restored = UniversalEventRecord.from_dict(data)
        assert restored.event_type == event.event_type
        assert restored.source == event.source


class TestEventLog:
    """Test event log functionality"""
    
    def test_event_log_creation(self):
        """Test creating event log"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test_events.jsonl"
            log = EventLog(log_path)
            assert log.log_path == log_path
    
    def test_append_and_read_events(self):
        """Test appending and reading events"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test_events.jsonl"
            log = EventLog(log_path)
            
            # Append events
            event1 = UniversalEventRecord(event_type="event1")
            event2 = UniversalEventRecord(event_type="event2")
            log.append(event1)
            log.append(event2)
            
            # Read all
            events = log.read_all()
            assert len(events) == 2
            assert events[0].event_type == "event1"
            assert events[1].event_type == "event2"
    
    def test_query_events(self):
        """Test querying events with filters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test_events.jsonl"
            log = EventLog(log_path)
            
            # Create events with different types and sources
            log.append(UniversalEventRecord(
                event_type="type_a",
                source=EventSource.USER_INPUT
            ))
            log.append(UniversalEventRecord(
                event_type="type_b",
                source=EventSource.DEVICE_LOG
            ))
            log.append(UniversalEventRecord(
                event_type="type_a",
                source=EventSource.DEVICE_LOG
            ))
            
            # Query by type
            type_a = log.query(event_type="type_a")
            assert len(type_a) == 2
            
            # Query by source
            user_input = log.query(source=EventSource.USER_INPUT)
            assert len(user_input) == 1


class TestIntentToken:
    """Test intent token functionality"""
    
    def test_create_intent(self):
        """Test creating intent token"""
        intent = IntentToken()
        assert intent.intent_id is not None
        assert intent.status == IntentStatus.FORMING
    
    def test_intent_lifecycle(self):
        """Test complete intent lifecycle"""
        intent = IntentToken()
        
        # Set pre-action
        intent.set_pre_action(
            goal="Test goal",
            constraints=["constraint1", "constraint2"],
            success_signals=["signal1"],
            confidence=0.8
        )
        assert intent.status == IntentStatus.READY
        assert intent.pre_action.goal == "Test goal"
        assert intent.pre_action.confidence == 0.8
        
        # Start execution
        intent.start_execution()
        assert intent.status == IntentStatus.EXECUTING
        
        # Set post-event
        intent.set_post_event(
            trigger="test_trigger",
            resulting_state={"key": "value"},
            payoff=0.9
        )
        assert intent.status == IntentStatus.COMPLETED
        assert intent.post_event.payoff == 0.9
        
        # Mark analyzed
        intent.mark_analyzed()
        assert intent.status == IntentStatus.ANALYZED
    
    def test_intent_success_calculation(self):
        """Test intent success calculation"""
        intent = IntentToken()
        intent.set_pre_action(goal="Test")
        intent.start_execution()
        
        # Positive payoff = success
        intent.set_post_event(
            trigger="trigger",
            resulting_state={},
            payoff=0.8
        )
        assert intent.calculate_success() is True
        
        # Test failed intent
        failed = IntentToken()
        failed.set_pre_action(goal="Test")
        failed.start_execution()
        failed.set_post_event(
            trigger="trigger",
            resulting_state={},
            payoff=-0.5
        )
        assert failed.calculate_success() is False
    
    def test_intent_serialization(self):
        """Test intent to/from dict"""
        intent = IntentToken()
        intent.set_pre_action(goal="Test", confidence=0.7)
        
        # To dict
        data = intent.to_dict()
        assert data['status'] == "ready"
        assert data['pre_action']['goal'] == "Test"
        
        # From dict
        restored = IntentToken.from_dict(data)
        assert restored.status == IntentStatus.READY
        assert restored.pre_action.goal == "Test"


class TestIntentRegistry:
    """Test intent registry functionality"""
    
    def test_register_and_get_intent(self):
        """Test registering and retrieving intent"""
        registry = IntentRegistry()
        intent = IntentToken()
        intent.set_pre_action(goal="Test")
        
        registry.register(intent)
        retrieved = registry.get(intent.intent_id)
        
        assert retrieved is not None
        assert retrieved.intent_id == intent.intent_id
    
    def test_query_by_status(self):
        """Test querying intents by status"""
        registry = IntentRegistry()
        
        # Create intents with different statuses
        ready_intent = IntentToken()
        ready_intent.set_pre_action(goal="Ready")
        
        completed_intent = IntentToken()
        completed_intent.set_pre_action(goal="Completed")
        completed_intent.start_execution()
        completed_intent.set_post_event(
            trigger="t", resulting_state={}, payoff=1.0
        )
        
        registry.register(ready_intent)
        registry.register(completed_intent)
        
        ready_list = registry.query_by_status(IntentStatus.READY)
        completed_list = registry.query_by_status(IntentStatus.COMPLETED)
        
        assert len(ready_list) == 1
        assert len(completed_list) == 1
    
    def test_success_rate(self):
        """Test calculating success rate"""
        registry = IntentRegistry()
        
        # Create successful intent
        success = IntentToken()
        success.set_pre_action(goal="Success")
        success.start_execution()
        success.set_post_event(
            trigger="t", resulting_state={}, payoff=1.0
        )
        
        # Create failed intent
        failure = IntentToken()
        failure.set_pre_action(goal="Failure")
        failure.start_execution()
        failure.set_post_event(
            trigger="t", resulting_state={}, payoff=-1.0
        )
        
        registry.register(success)
        registry.register(failure)
        
        rate = registry.get_success_rate()
        assert rate == 0.5


class TestHypothesis:
    """Test hypothesis and parallel model functionality"""
    
    def test_create_hypothesis(self):
        """Test creating hypothesis"""
        hypothesis = Hypothesis(
            name="Test hypothesis",
            description="Testing hypothesis creation"
        )
        
        assert hypothesis.hypothesis_id is not None
        assert hypothesis.name == "Test hypothesis"
    
    def test_add_parallel_models(self):
        """Test adding models from different perspectives"""
        hypothesis = Hypothesis(name="Multi-perspective")
        
        # Add ME model
        me_model = hypothesis.add_model(
            perspective=ModelPerspective.ME,
            description="My perspective",
            probability=0.8
        )
        assert me_model.perspective == ModelPerspective.ME
        
        # Add SYSTEM model
        sys_model = hypothesis.add_model(
            perspective=ModelPerspective.SYSTEM,
            description="System perspective",
            probability=0.6
        )
        assert sys_model.perspective == ModelPerspective.SYSTEM
        
        # Verify both stored
        assert len(hypothesis.models) == 2
    
    def test_consensus_probability(self):
        """Test consensus probability calculation"""
        hypothesis = Hypothesis(name="Consensus test")
        hypothesis.add_model(
            perspective=ModelPerspective.ME,
            description="ME perspective",
            probability=0.8
        )
        hypothesis.add_model(
            perspective=ModelPerspective.WE,
            description="WE perspective",
            probability=0.6
        )
        
        consensus = hypothesis.get_consensus_probability()
        assert consensus == 0.7  # Average of 0.8 and 0.6
    
    def test_perspective_divergence(self):
        """Test perspective divergence calculation"""
        hypothesis = Hypothesis(name="Divergence test")
        hypothesis.add_model(
            perspective=ModelPerspective.ME,
            description="ME perspective",
            probability=0.9
        )
        hypothesis.add_model(
            perspective=ModelPerspective.THEY,
            description="THEY perspective",
            probability=0.1
        )
        
        divergence = hypothesis.get_perspective_divergence()
        assert divergence > 0.3  # High divergence
    
    def test_falsifiers(self):
        """Test adding and checking falsifiers"""
        hypothesis = Hypothesis(name="Falsifier test")
        model = hypothesis.add_model(
            perspective=ModelPerspective.ME,
            description="ME perspective",
            probability=0.8
        )
        
        # Add falsifier
        falsifier = model.add_falsifier(
            condition="Test condition fails",
            test_procedure="Run test X"
        )
        
        assert len(model.falsifiers) == 1
        assert not model.is_falsified()
        
        # Mark as falsified
        falsifier.tested = True
        falsifier.test_result = True
        assert model.is_falsified()
    
    def test_hypothesis_serialization(self):
        """Test hypothesis to/from dict"""
        hypothesis = Hypothesis(name="Serialization test")
        hypothesis.add_model(
            perspective=ModelPerspective.ME,
            description="ME perspective",
            probability=0.7
        )
        
        # To dict
        data = hypothesis.to_dict()
        assert data['name'] == "Serialization test"
        assert len(data['models']) == 1
        
        # From dict
        restored = Hypothesis.from_dict(data)
        assert restored.name == hypothesis.name
        assert len(restored.models) == 1


class TestTestObject:
    """Test test object functionality"""
    
    def test_create_test(self):
        """Test creating test object"""
        test = TestObject(
            name="Test name",
            description="Test description",
            test_type=TestType.USER_DRIVEN
        )
        
        assert test.test_id is not None
        assert test.name == "Test name"
        assert test.test_type == TestType.USER_DRIVEN
    
    def test_link_hypothesis(self):
        """Test linking test to hypothesis"""
        test = TestObject(name="Linked test")
        hypothesis = Hypothesis(name="Target hypothesis")
        
        test.link_hypothesis(hypothesis.hypothesis_id)
        
        assert hypothesis.hypothesis_id in test.hypothesis_ids
    
    def test_execute_test_success(self):
        """Test executing test with success"""
        test = TestObject(name="Success test")
        
        def success_function():
            return {
                'passed': True,
                'measurements': {'value': 100},
                'observations': ['Good result']
            }
        
        result = test.execute(success_function)
        
        assert result.status == TestStatus.PASSED
        assert result.passed is True
        assert result.measurements['value'] == 100
        assert len(result.observations) == 1
        assert test.status == TestStatus.PASSED
    
    def test_execute_test_failure(self):
        """Test executing test with failure"""
        test = TestObject(name="Failure test")
        
        def failure_function():
            return {'passed': False}
        
        result = test.execute(failure_function)
        
        assert result.status == TestStatus.FAILED
        assert result.passed is False
    
    def test_execute_test_error(self):
        """Test executing test with error"""
        test = TestObject(name="Error test")
        
        def error_function():
            raise ValueError("Test error")
        
        result = test.execute(error_function)
        
        assert result.status == TestStatus.ERROR
        assert result.error_message == "Test error"
    
    def test_success_rate(self):
        """Test calculating test success rate"""
        test = TestObject(name="Rate test")
        
        # Execute multiple times
        test.execute(lambda: True)  # Success
        test.execute(lambda: True)  # Success
        test.execute(lambda: False)  # Failure
        
        rate = test.get_success_rate()
        assert rate == pytest.approx(0.666, abs=0.01)


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_workflow(self):
        """Test complete HandshakeOS-E workflow"""
        # 1. Record initial event
        with tempfile.TemporaryDirectory() as tmpdir:
            log = EventLog(Path(tmpdir) / "events.jsonl")
            
            event = UniversalEventRecord(
                event_type="performance_concern",
                payload={"metric": "latency", "value": 250},
                source=EventSource.DEVICE_LOG
            )
            log.append(event)
            
            # 2. Create intent to address
            intent = IntentToken()
            intent.set_pre_action(
                goal="Reduce latency to <100ms",
                constraints=["No breaking changes"],
                success_signals=["Latency < 100ms"],
                confidence=0.7
            )
            
            # 3. Create hypothesis
            hypothesis = Hypothesis(
                name="Caching hypothesis",
                description="Caching will reduce latency"
            )
            me_model = hypothesis.add_model(
                perspective=ModelPerspective.ME,
                description="ME perspective model",
                probability=0.8
            )
            me_model.add_falsifier(
                condition="Latency doesn't improve"
            )
            
            # 4. Create and execute test
            test = TestObject(
                name="Cache test",
                test_type=TestType.USER_DRIVEN
            )
            test.link_hypothesis(hypothesis.hypothesis_id)
            
            def cache_test():
                return {
                    'passed': True,
                    'measurements': {'latency': 85},
                    'observations': ['Significant improvement']
                }
            
            result = test.execute(cache_test)
            
            # 5. Complete intent
            intent.start_execution()
            intent.set_post_event(
                trigger="Performance optimization",
                resulting_state={"latency": 85},
                payoff=0.9
            )
            
            # 6. Update hypothesis
            me_model.update_probability(0.95, basis="Test confirmed")
            me_model.add_evidence(event.event_id, supports=True)
            
            # 7. Record completion
            completion = UniversalEventRecord(
                event_type="optimization_complete",
                payload={"improvement": "66%"},
                source=EventSource.USER_TEST,
                related_events=[event.event_id],
                related_intents=[intent.intent_id],
                related_hypotheses=[hypothesis.hypothesis_id]
            )
            log.append(completion)
            
            # Verify workflow
            assert result.passed is True
            assert intent.calculate_success() is True
            assert me_model.probability == 0.95
            assert len(log.read_all()) == 2
    
    def test_registries_integration(self):
        """Test using all registries together"""
        intent_reg = IntentRegistry()
        hyp_reg = HypothesisRegistry()
        test_reg = TestRegistry()
        
        # Create objects
        intent = IntentToken()
        intent.set_pre_action(goal="Test integration")
        
        hypothesis = Hypothesis(name="Integration hypothesis")
        hypothesis.add_model(
            perspective=ModelPerspective.SYSTEM,
            description="System perspective",
            probability=0.7
        )
        
        test = TestObject(name="Integration test")
        test.link_hypothesis(hypothesis.hypothesis_id)
        hypothesis.add_test_link(test.test_id)
        
        # Register all
        intent_reg.register(intent)
        hyp_reg.register(hypothesis)
        test_reg.register(test)
        
        # Verify cross-references
        retrieved_hyp = hyp_reg.get(hypothesis.hypothesis_id)
        assert test.test_id in retrieved_hyp.related_tests
        
        tests_for_hyp = test_reg.query_by_hypothesis(hypothesis.hypothesis_id)
        assert len(tests_for_hyp) == 1
        assert tests_for_hyp[0].test_id == test.test_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
