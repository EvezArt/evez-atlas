#!/usr/bin/env python3
"""
HandshakeOS-E Nervous System Demo

Demonstrates the complete architecture:
- Universal event recording
- Intent token lifecycle
- Parallel hypothesis tracking
- Test execution and evidence gathering
"""

import time
from pathlib import Path

from src.handshakeos import (
    UniversalEventRecord,
    EventSource,
    DomainMixtureVector,
    IntentToken,
    Hypothesis,
    ModelPerspective,
    TestObject,
    TestType,
)
from src.handshakeos.event_record import EventLog
from src.handshakeos.intent_token import IntentRegistry
from src.handshakeos.hypothesis import HypothesisRegistry
from src.handshakeos.test_object import TestRegistry


def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_complete_workflow():
    """Run complete workflow demonstration"""
    print_section("HandshakeOS-E Nervous System Demo")
    
    # Create log and registries
    log = EventLog()
    print(f"📝 Event log: {log.log_path}\n")
    
    # 1. Create initial event
    print("1️⃣  Recording performance concern event...")
    event1 = UniversalEventRecord(
        event_type="performance_concern",
        payload={"metric": "response_time", "value_ms": 450},
        source=EventSource.DEVICE_LOG
    )
    log.append(event1)
    print(f"   ✓ Event recorded: {event1.event_id[:8]}...\n")
    
    # 2. Create intent
    print("2️⃣  Creating optimization intent...")
    intent = IntentToken()
    intent.set_pre_action(
        goal="Reduce response time to <200ms",
        constraints=["No breaking changes"],
        success_signals=["Response time < 200ms"],
        confidence=0.7
    )
    print(f"   ✓ Intent created: {intent.intent_id[:8]}...")
    print(f"   Goal: {intent.pre_action.goal}\n")
    
    # 3. Create hypothesis with multiple perspectives
    print("3️⃣  Creating hypothesis with parallel models...")
    hypothesis = Hypothesis(
        name="Caching Optimization",
        description="Caching will reduce response time"
    )
    
    me_model = hypothesis.add_model(
        perspective=ModelPerspective.ME,
        description="I believe caching will help",
        probability=0.85
    )
    me_model.add_falsifier(condition="No improvement after caching")
    
    sys_model = hypothesis.add_model(
        perspective=ModelPerspective.SYSTEM,
        description="System metrics suggest infrastructure limits",
        probability=0.60
    )
    
    print(f"   ✓ Hypothesis: {hypothesis.hypothesis_id[:8]}...")
    print(f"   Models: {len(hypothesis.models)}")
    print(f"   Consensus probability: {hypothesis.get_consensus_probability():.2f}\n")
    
    # 4. Create and execute test
    print("4️⃣  Creating and executing test...")
    test = TestObject(
        name="Cache Performance Test",
        test_type=TestType.USER_DRIVEN
    )
    test.link_hypothesis(hypothesis.hypothesis_id)
    
    def cache_test():
        time.sleep(0.1)
        return {
            'passed': True,
            'measurements': {'response_time_ms': 180, 'improvement_pct': 60},
            'observations': ['Significant improvement', 'No errors']
        }
    
    result = test.execute(cache_test)
    print(f"   ✓ Test executed: {result.status.value}")
    print(f"   Result: {result.passed}")
    print(f"   Measurements: {result.measurements}\n")
    
    # 5. Complete intent with post-event
    print("5️⃣  Completing intent with post-event data...")
    intent.start_execution()
    intent.set_post_event(
        trigger="Performance optimization",
        resulting_state={"response_time_ms": 180},
        payoff=0.9
    )
    print(f"   ✓ Intent status: {intent.status.value}")
    print(f"   Success: {intent.calculate_success()}\n")
    
    # 6. Update hypothesis based on evidence
    print("6️⃣  Updating hypothesis with test evidence...")
    me_model.update_probability(0.95, basis="Test confirmed")
    print(f"   Updated ME model probability: {me_model.probability}")
    print(f"   New consensus: {hypothesis.get_consensus_probability():.2f}\n")
    
    # 7. Create completion event with all links
    print("7️⃣  Recording completion event...")
    completion = UniversalEventRecord(
        event_type="optimization_complete",
        payload={"improvement_pct": 60, "final_ms": 180},
        source=EventSource.USER_TEST,
        related_events=[event1.event_id],
        related_intents=[intent.intent_id],
        related_hypotheses=[hypothesis.hypothesis_id]
    )
    log.append(completion)
    print(f"   ✓ Completion event: {completion.event_id[:8]}...\n")
    
    # Summary
    print_section("Summary")
    print("✅ Successfully demonstrated:")
    print("   • Universal event recording")
    print("   • Intent token lifecycle")
    print("   • Parallel hypothesis tracking")
    print("   • Test execution")
    print("   • Complete workflow integration\n")
    
    print("📊 Final State:")
    print(f"   Events: {len(log.read_all())}")
    print(f"   Intent success: {intent.calculate_success()}")
    print(f"   Hypothesis consensus: {hypothesis.get_consensus_probability():.2f}")
    print(f"   Test passed: {result.passed}\n")


if __name__ == "__main__":
    demo_complete_workflow()
    print("✨ Demo complete!\n")
