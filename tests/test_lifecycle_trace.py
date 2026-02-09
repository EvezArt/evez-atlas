#!/usr/bin/env python3
"""
Test: Entity Lifecycle Root Trace Integration

Tests the deep connection between entity lifecycle and root trace system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'recursive-observer', 'src'))

from skills.entity_lifecycle import EntityLifecycleManager
from recursive_observer.tracer import trace_execution, get_lifecycle_events, clear_lifecycle_events


def test_lifecycle_trace_integration():
    """Test that lifecycle events are captured in root trace."""
    
    def lifecycle_ops():
        manager = EntityLifecycleManager(state_file='/tmp/test_lifecycle_trace.jsonl')
        entity = manager.create_entity('test_entity', 'tester', 'test_domain')
        manager.awaken_entity('test_entity')
        return entity
    
    # Trace the lifecycle operations
    trace = trace_execution(lifecycle_ops)
    
    # Verify trace has lifecycle events
    assert trace.lifecycle_events is not None, "Lifecycle events should be captured"
    assert len(trace.lifecycle_events) == 3, "Should have exactly 3 lifecycle events (create, awakening, activated)"
    
    # Verify event types
    event_types = [e['event_type'] for e in trace.lifecycle_events]
    assert 'entity_created' in event_types, "Should have entity_created event"
    assert 'entity_awakening' in event_types, "Should have entity_awakening event"
    assert 'entity_activated' in event_types, "Should have entity_activated event"
    
    # Verify entity IDs are captured
    entity_ids = [e['entity_id'] for e in trace.lifecycle_events]
    assert 'test_entity' in entity_ids, "Entity ID should be in lifecycle events"
    
    print("✅ test_lifecycle_trace_integration passed")


def test_lifecycle_event_recording():
    """Test that lifecycle events are recorded properly."""
    clear_lifecycle_events()
    
    manager = EntityLifecycleManager(state_file='/tmp/test_event_recording.jsonl')
    
    # Create entity
    manager.create_entity('recorder_test', 'recorder', 'test')
    events = get_lifecycle_events()
    assert len(events) == 1, "Should have 1 event after creation"
    assert events[0]['event_type'] == 'entity_created'
    
    # Awaken entity
    manager.awaken_entity('recorder_test')
    events = get_lifecycle_events()
    assert len(events) == 3, "Should have 3 events after awakening (create, awakening, activated)"
    
    # Hibernate entity
    manager.hibernate_entity('recorder_test', depth=1)
    events = get_lifecycle_events()
    assert len(events) == 4, "Should have 4 events after hibernation"
    assert events[-1]['event_type'] == 'entity_hibernated'
    
    print("✅ test_lifecycle_event_recording passed")


def test_quantum_entanglement_trace():
    """Test that quantum entanglement is traced."""
    clear_lifecycle_events()
    
    manager = EntityLifecycleManager(state_file='/tmp/test_quantum_trace.jsonl')
    manager.create_entity('quantum_test', 'quantum_agent', 'quantum')
    manager.quantum_entangle('quantum_test', 'quantum_realm')
    
    events = get_lifecycle_events()
    quantum_events = [e for e in events if e['event_type'] == 'entity_quantum_entangled']
    assert len(quantum_events) == 1, "Should have 1 quantum entanglement event"
    assert quantum_events[0]['metadata']['quantum_entangled'] == True
    assert quantum_events[0]['metadata']['domain'] == 'quantum_realm'
    
    print("✅ test_quantum_entanglement_trace passed")


def test_error_correction_trace():
    """Test that error correction mode is traced."""
    clear_lifecycle_events()
    
    manager = EntityLifecycleManager(state_file='/tmp/test_error_trace.jsonl')
    manager.create_entity('error_test', 'error_prone', 'test')
    manager.error_correction_mode('error_test')
    
    events = get_lifecycle_events()
    error_events = [e for e in events if e['event_type'] == 'entity_error_correction']
    assert len(error_events) == 1, "Should have 1 error correction event"
    assert error_events[0]['state'] == 'error_correction'
    assert error_events[0]['metadata']['error_count'] == 1
    
    print("✅ test_error_correction_trace passed")


def run_all_tests():
    """Run all lifecycle trace integration tests."""
    print("=" * 70)
    print("🧪 RUNNING LIFECYCLE TRACE INTEGRATION TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_lifecycle_trace_integration,
        test_lifecycle_event_recording,
        test_quantum_entanglement_trace,
        test_error_correction_trace,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"📊 TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
