#!/usr/bin/env python3
"""
HandshakeOS-E Nervous System Demonstration

This script demonstrates the key features of the nervous system:
1. Universal event recording with intent and readout
2. Parallel hypothesis tracking (me/we/they/system models)
3. Test linkage to hypotheses
4. Attribution and auditability
5. Domain-agnostic mixture vectors

Run this to see the system in action.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mastra.nervous_system import (
    NervousSystem,
    Actor,
    IntentToken,
    EventReadout,
    MixtureVector,
    ModelType,
)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_basic_event_recording():
    """Demonstrate basic event recording."""
    print_section("1. Basic Event Recording")
    
    # Initialize nervous system
    ns = NervousSystem(Path("data/nervous_system_demo"))
    
    # Register an actor
    actor = Actor(
        name="Demo Agent",
        type="agent",
        permissions={"record_events", "create_hypotheses"}
    )
    ns.register_actor(actor)
    print(f"✓ Registered actor: {actor.name} (ID: {actor.id[:8]}...)")
    
    # Record event with intent
    intent = IntentToken(
        goal="Process user request",
        constraints=["Must complete within 5 seconds", "No external API calls"],
        success_metric="Request processed successfully",
        confidence=0.8
    )
    
    event = ns.record_event(
        actor_id=actor.id,
        intent=intent,
        metadata={"request_type": "data_query"}
    )
    print(f"✓ Recorded event with intent: {event.id[:8]}...")
    print(f"  Goal: {intent.goal}")
    print(f"  Confidence: {intent.confidence}")
    
    # Update event with readout
    readout = EventReadout(
        trigger="user_request",
        result_state={"status": "success", "items_processed": 42},
        policy_used="default_query_policy",
        payoff=1.0,
        success=True
    )
    
    ns.update_event(event.id, readout=readout)
    print(f"✓ Updated event with readout")
    print(f"  Success: {readout.success}")
    print(f"  Payoff: {readout.payoff}")
    
    return ns, actor


def demo_mixture_vectors(ns: NervousSystem, actor: Actor):
    """Demonstrate domain-agnostic mixture vectors."""
    print_section("2. Domain-Agnostic Mixture Vectors")
    
    # Create mixture vector that emerges from event characteristics
    mixture = MixtureVector(
        components={
            "computation": 0.3,
            "user_interaction": 0.5,
            "data_access": 0.2
        }
    )
    mixture.normalize()
    
    print("✓ Created mixture vector (emergent domain signature):")
    for component, weight in mixture.components.items():
        print(f"  {component}: {weight:.2f}")
    
    # Record event with mixture
    intent = IntentToken(
        goal="Hybrid operation: compute and respond",
        confidence=0.75
    )
    
    event = ns.record_event(
        actor_id=actor.id,
        intent=intent,
        mixture=mixture,
        metadata={"type": "hybrid_operation"}
    )
    
    print(f"✓ Recorded event with mixture: {event.id[:8]}...")
    
    return event


def demo_parallel_hypotheses(ns: NervousSystem):
    """Demonstrate parallel hypothesis tracking."""
    print_section("3. Parallel Hypothesis Tracking")
    
    # Create hypotheses for each model type
    hypotheses = {}
    
    # ME model: Self-understanding
    hypotheses['me'] = ns.create_hypothesis(
        model_type=ModelType.ME,
        description="I can process user requests within 5 seconds 90% of the time",
        probability=0.85,
        falsifiers=["Average processing time exceeds 5 seconds over 100 requests"],
        mixture=MixtureVector(components={"performance": 0.8, "reliability": 0.2})
    )
    print(f"✓ ME model hypothesis: {hypotheses['me'].description}")
    print(f"  Probability: {hypotheses['me'].probability}")
    
    # WE model: Team/collective understanding
    hypotheses['we'] = ns.create_hypothesis(
        model_type=ModelType.WE,
        description="Our system handles peak load of 1000 req/s with <100ms latency",
        probability=0.70,
        falsifiers=["Latency exceeds 100ms at 1000 req/s", "System crashes under load"],
        mixture=MixtureVector(components={"scalability": 0.6, "coordination": 0.4})
    )
    print(f"✓ WE model hypothesis: {hypotheses['we'].description}")
    print(f"  Probability: {hypotheses['we'].probability}")
    
    # THEY model: External agents/users
    hypotheses['they'] = ns.create_hypothesis(
        model_type=ModelType.THEY,
        description="Users prefer brief responses over detailed explanations",
        probability=0.60,
        falsifiers=["User satisfaction drops with brief responses"],
        mixture=MixtureVector(components={"user_behavior": 0.9, "preferences": 0.1})
    )
    print(f"✓ THEY model hypothesis: {hypotheses['they'].description}")
    print(f"  Probability: {hypotheses['they'].probability}")
    
    # SYSTEM model: Environment/infrastructure
    hypotheses['system'] = ns.create_hypothesis(
        model_type=ModelType.SYSTEM,
        description="Database connection pool of 20 is sufficient for current load",
        probability=0.75,
        falsifiers=["Connection pool exhaustion events", "Request queuing > 1 second"],
        mixture=MixtureVector(components={"infrastructure": 0.7, "resources": 0.3})
    )
    print(f"✓ SYSTEM model hypothesis: {hypotheses['system'].description}")
    print(f"  Probability: {hypotheses['system'].probability}")
    
    return hypotheses


def demo_test_linkage(ns: NervousSystem, hypotheses: dict):
    """Demonstrate test linkage to hypotheses."""
    print_section("4. Test Linkage to Hypotheses")
    
    # Create test for ME model hypothesis
    test_me = ns.create_test(
        name="Test: Average processing time",
        hypothesis_id=hypotheses['me'].id,
        test_code="""
def test_processing_time():
    times = measure_processing_times(n=100)
    avg_time = sum(times) / len(times)
    assert avg_time < 5.0, f"Average time {avg_time}s exceeds 5s"
        """,
        metadata={"test_type": "performance"}
    )
    print(f"✓ Created test for ME hypothesis: {test_me.name}")
    
    # Record test result
    ns.record_test_result(
        test_id=test_me.id,
        passed=True,
        result={"average_time": 4.2, "samples": 100}
    )
    print(f"  Test passed: average time = 4.2s")
    
    # Create test for SYSTEM hypothesis
    test_system = ns.create_test(
        name="Test: Connection pool utilization",
        hypothesis_id=hypotheses['system'].id,
        test_code="""
def test_connection_pool():
    metrics = monitor_connection_pool(duration=60)
    max_used = metrics['max_connections_used']
    assert max_used <= 20, f"Pool of 20 insufficient (max used: {max_used})"
        """,
        metadata={"test_type": "infrastructure"}
    )
    print(f"✓ Created test for SYSTEM hypothesis: {test_system.name}")
    
    # Record test result
    ns.record_test_result(
        test_id=test_system.id,
        passed=True,
        result={"max_connections_used": 18, "duration_seconds": 60}
    )
    print(f"  Test passed: max connections used = 18/20")
    
    return test_me, test_system


def demo_attribution_and_audit(ns: NervousSystem, event, test):
    """Demonstrate attribution and auditability."""
    print_section("5. Attribution and Auditability")
    
    # Get attribution for an event
    attribution = ns.get_attribution(event.id)
    print(f"✓ Attribution for event {event.id[:8]}...")
    print(f"  Actor: {attribution['actor']['name']}")
    print(f"  Created: {attribution['created_at']}")
    print(f"  Version: {attribution['version']}")
    
    # Get audit trail
    trail = ns.get_audit_trail(event.id)
    print(f"\n✓ Audit trail for event {event.id[:8]}...")
    print(f"  Total versions: {len(trail)}")
    for i, version in enumerate(trail, 1):
        print(f"  Version {i}: {version['updated_at'][:19]}")
    
    # Get test audit trail
    test_trail = ns.get_audit_trail(test.id)
    print(f"\n✓ Audit trail for test {test.id[:8]}...")
    print(f"  Total versions: {len(test_trail)}")
    print(f"  Test executed: {test_trail[-1].get('executed_at', 'N/A')[:19]}")


def demo_queries(ns: NervousSystem, actor: Actor):
    """Demonstrate query capabilities."""
    print_section("6. Query and Analysis")
    
    # Query events by actor
    actor_events = ns.query_events(actor_id=actor.id)
    print(f"✓ Events by actor '{actor.name}': {len(actor_events)}")
    
    # Get hypotheses by model type
    me_hypotheses = ns.get_hypotheses_by_model(ModelType.ME)
    we_hypotheses = ns.get_hypotheses_by_model(ModelType.WE)
    print(f"✓ ME model hypotheses: {len(me_hypotheses)}")
    print(f"✓ WE model hypotheses: {len(we_hypotheses)}")
    
    # Get system statistics
    stats = ns.get_stats()
    print(f"\n✓ System Statistics:")
    print(f"  Total events: {stats['total_events']}")
    print(f"  Total hypotheses: {stats['total_hypotheses']}")
    print(f"  Total tests: {stats['total_tests']}")
    print(f"  Total actors: {stats['total_actors']}")
    print(f"\n  Hypotheses by model:")
    for model, count in stats['hypotheses_by_model'].items():
        print(f"    {model}: {count}")


def demo_rollback_scenario(ns: NervousSystem, actor: Actor):
    """Demonstrate rollback capability through versioning."""
    print_section("7. Rollback Capability (via Versioning)")
    
    # Create an event
    intent = IntentToken(
        goal="Test rollback capability",
        confidence=0.9
    )
    
    event = ns.record_event(
        actor_id=actor.id,
        intent=intent
    )
    print(f"✓ Created event: {event.id[:8]}... (version {event.version})")
    
    # Update multiple times
    for i in range(3):
        readout = EventReadout(
            trigger=f"update_{i+1}",
            result_state={"iteration": i+1},
            success=True
        )
        event = ns.update_event(event.id, readout=readout)
        print(f"  Updated to version {event.version}")
    
    # Show audit trail (enables rollback)
    trail = ns.get_audit_trail(event.id)
    print(f"\n✓ Complete audit trail (enables rollback):")
    for i, version in enumerate(trail):
        print(f"  Version {version['version']}: {version['updated_at'][:19]}")
    
    print(f"\n  Any version can be restored from the audit trail")
    print(f"  Current version: {event.version}")


def main():
    """Run complete demonstration."""
    print("\n" + "="*60)
    print("  HandshakeOS-E Nervous System Demonstration")
    print("="*60)
    print("\nThis demonstration shows:")
    print("  • Universal event recording with intent/readout")
    print("  • Domain-agnostic mixture vectors")
    print("  • Parallel hypothesis tracking (me/we/they/system)")
    print("  • Test linkage to hypotheses")
    print("  • Complete attribution and auditability")
    print("  • Rollback capability via versioning")
    
    # Run demonstrations
    ns, actor = demo_basic_event_recording()
    event = demo_mixture_vectors(ns, actor)
    hypotheses = demo_parallel_hypotheses(ns)
    test_me, test_system = demo_test_linkage(ns, hypotheses)
    demo_attribution_and_audit(ns, event, test_me)
    demo_queries(ns, actor)
    demo_rollback_scenario(ns, actor)
    
    # Final summary
    print_section("Summary")
    stats = ns.get_stats()
    print("✓ Demonstration complete!")
    print(f"\nGenerated:")
    print(f"  • {stats['total_events']} events")
    print(f"  • {stats['total_hypotheses']} hypotheses")
    print(f"  • {stats['total_tests']} tests")
    print(f"  • {stats['total_actors']} actors")
    print(f"\nAll data stored in: {ns.data_dir}")
    print("\nKey principles demonstrated:")
    print("  ✓ Universal, domain-agnostic event records")
    print("  ✓ Explicit intent and readout tracking")
    print("  ✓ Parallel model tracking (me/we/they/system)")
    print("  ✓ Test-hypothesis linkage")
    print("  ✓ Full attribution (no invisible agents)")
    print("  ✓ Complete auditability")
    print("  ✓ Rollback capability via versioning")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
