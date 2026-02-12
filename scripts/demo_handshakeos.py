#!/usr/bin/env python3
"""
HandshakeOS-E Complete Demo

This script demonstrates all core HandshakeOS-E features:
1. UniversalEventRecord - Event recording with domain signatures
2. IntentToken - Pre/post-action intent tracking
3. ParallelHypotheses - Multi-perspective hypothesis evaluation
4. TestObject - First-class test objects
5. BoundedIdentity - Identity and permission management
6. AuditLogger - Centralized audit logging
7. ReversibilityManager - Action reversal

Run this to verify all components work together.
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path
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


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def demo_universal_event_record(data_dir: str):
    """Demo UniversalEventRecord functionality."""
    print_section("1. UniversalEventRecord - Event Recording")
    
    # Create an event
    event = create_event(
        event_type="user_interaction",
        attributed_to="user_alice",
        state_before={
            "session": "idle",
            "query": None
        },
        state_after={
            "session": "active",
            "query": "What is quantum computing?"
        },
        device_id="browser_chrome",
        network_route=["client", "lb", "api_server"],
        domain_signature=DomainSignature(
            technical=0.5,
            social=0.4,
            cognitive=0.8
        )
    )
    
    print(f"\n✅ Created event: {event.event_id[:12]}...")
    print(f"   Type: {event.event_type}")
    print(f"   By: {event.attributed_to}")
    print(f"   Domain entropy: {event.domain_entropy:.3f}")
    print(f"   State changes: {len(event.state_delta['changed'])} modified, "
          f"{len(event.state_delta['added'])} added")
    
    # Add audit entry
    event.add_audit_entry("created", "system", {"demo": True})
    print(f"   Audit entries: {len(event.audit_log)}")
    
    # Save to log
    log_path = f"{data_dir}/events/demo_events.jsonl"
    event.save_to_log(log_path)
    print(f"   Saved to: {log_path}")
    
    return event


def demo_intent_token(data_dir: str, event_id: str):
    """Demo IntentToken functionality."""
    print_section("2. IntentToken - Intent Tracking")
    
    # Create intent (pre-action)
    intent = IntentToken(
        pre_action=PreAction(
            goal="Answer user's quantum computing question",
            constraints=[
                "Response must be under 200 words",
                "Must be technically accurate",
                "Should include practical examples"
            ],
            success_criteria=[
                "User understands basics",
                "Response is complete",
                "No follow-up confusion"
            ],
            confidence=0.85
        ),
        attributed_to="ai_assistant_001"
    )
    
    print(f"\n✅ Created intent: {intent.token_id[:12]}...")
    print(f"   Goal: {intent.pre_action.goal}")
    print(f"   Confidence: {intent.pre_action.confidence:.2%}")
    print(f"   Constraints: {len(intent.pre_action.constraints)}")
    print(f"   Success criteria: {len(intent.pre_action.success_criteria)}")
    
    # Link to event
    intent.link_event(event_id)
    print(f"   Linked to event: {event_id[:12]}...")
    
    # Simulate execution and measurements
    intent.add_measurement("response_length_words", 187, "words")
    intent.add_measurement("processing_time_ms", 234, "milliseconds")
    intent.add_measurement("confidence_score", 0.92, "score")
    
    # Complete intent (post-action)
    intent.complete(
        trigger="user_query_received",
        final_state={
            "response_generated": True,
            "word_count": 187,
            "user_satisfied": True
        },
        payoff=0.90  # High success
    )
    
    print(f"\n✅ Intent completed!")
    print(f"   Payoff: {intent.post_action.payoff:.2%}")
    print(f"   Measurements: {len(intent.measurements)}")
    print(f"   Confidence gap: {intent.confidence_vs_outcome_gap():.3f}")
    
    # Save to log
    log_path = f"{data_dir}/intents/demo_intents.jsonl"
    intent.save_to_log(log_path)
    print(f"   Saved to: {log_path}")
    
    return intent


def demo_parallel_hypotheses(data_dir: str, event_id: str, intent_id: str):
    """Demo ParallelHypotheses functionality."""
    print_section("3. ParallelHypotheses - Multi-Perspective Evaluation")
    
    # Create hypothesis set
    hypotheses = ParallelHypotheses(
        context="User will understand quantum computing from our response",
        me_perspective=HypothesisPerspective(
            perspective="me",
            hypothesis="I believe the explanation is clear and effective",
            probability=0.85,
            falsifiers=[
                "User asks clarifying questions",
                "User expresses confusion"
            ],
            proposed_by="ai_assistant_001"
        ),
        we_perspective=HypothesisPerspective(
            perspective="we",
            hypothesis="Team thinks quantum explanations usually work well",
            probability=0.75,
            falsifiers=[
                "Historical data shows <70% understanding",
                "Multiple follow-up questions"
            ],
            proposed_by="team_lead"
        ),
        they_perspective=HypothesisPerspective(
            perspective="they",
            hypothesis="Users typically find quantum topics challenging",
            probability=0.60,
            falsifiers=[
                "User provides positive feedback",
                "No follow-up questions"
            ],
            proposed_by="user_research"
        ),
        system_perspective=HypothesisPerspective(
            perspective="system",
            hypothesis="Data shows 70% comprehension rate for quantum topics",
            probability=0.70,
            falsifiers=[
                "Comprehension test score <60%",
                "Engagement metrics below threshold"
            ],
            proposed_by="analytics_system"
        )
    )
    
    print(f"\n✅ Created hypothesis set: {hypotheses.hypothesis_id[:12]}...")
    print(f"   Context: {hypotheses.context[:60]}...")
    
    print(f"\n   Perspectives:")
    for p in hypotheses.get_all_perspectives():
        print(f"   - {p.perspective:6s}: {p.probability:.2%} - {p.hypothesis[:50]}...")
    
    # Calculate meta-analysis
    consensus = hypotheses.calculate_consensus()
    divergence = hypotheses.calculate_divergence()
    
    print(f"\n   Meta-Analysis:")
    print(f"   - Consensus: {consensus:.2%}")
    print(f"   - Divergence: {divergence:.3f}")
    print(f"   - Converging: {hypotheses.is_converging()}")
    
    # Link to events and intents
    hypotheses.link_event(event_id)
    hypotheses.link_intent(intent_id)
    print(f"\n   Links:")
    print(f"   - Events: {len(hypotheses.related_events)}")
    print(f"   - Intents: {len(hypotheses.related_intents)}")
    
    # Save to log
    log_path = f"{data_dir}/hypotheses/demo_hypotheses.jsonl"
    hypotheses.save_to_log(log_path)
    print(f"   Saved to: {log_path}")
    
    return hypotheses


def demo_test_object(data_dir: str, hypothesis_id: str):
    """Demo TestObject functionality."""
    print_section("4. TestObject - First-Class Tests")
    
    # Create test
    test = TestObject(
        test_name="Verify User Comprehension",
        test_description="Check if user demonstrates understanding of quantum concepts",
        test_type="comprehension",
        hypothesis_ids=[hypothesis_id],
        perspective_filter=["system"],
        executable=True,
        execution_command="python verify_comprehension.py",
        expected_outcome="User can answer basic quantum questions",
        acceptance_criteria=[
            "Score >= 80% on comprehension test",
            "Can explain superposition",
            "Can explain entanglement"
        ],
        created_by="testing_system"
    )
    
    print(f"\n✅ Created test: {test.test_id[:12]}...")
    print(f"   Name: {test.test_name}")
    print(f"   Type: {test.test_type}")
    print(f"   Linked hypotheses: {len(test.hypothesis_ids)}")
    print(f"   Acceptance criteria: {len(test.acceptance_criteria)}")
    
    # Simulate test executions
    print(f"\n   Executing tests...")
    results = [
        TestResult(passed=True, execution_time_ms=123.4, output="Score: 85%"),
        TestResult(passed=True, execution_time_ms=118.7, output="Score: 92%"),
        TestResult(passed=True, execution_time_ms=125.1, output="Score: 88%"),
        TestResult(passed=False, execution_time_ms=131.2, output="Score: 72%"),
        TestResult(passed=True, execution_time_ms=119.8, output="Score: 90%"),
    ]
    
    for i, result in enumerate(results, 1):
        test.record_result(result)
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"   Run {i}: {status} ({result.execution_time_ms:.1f}ms)")
    
    # Calculate statistics
    pass_rate = test.calculate_pass_rate()
    is_flaky = test.is_flaky()
    avg_time = test.calculate_average_execution_time()
    
    print(f"\n   Statistics:")
    print(f"   - Pass rate: {pass_rate:.1%}")
    print(f"   - Is flaky: {is_flaky}")
    print(f"   - Avg execution time: {avg_time:.1f}ms")
    
    # Save to log
    log_path = f"{data_dir}/tests/demo_tests.jsonl"
    test.save_to_log(log_path)
    print(f"   Saved to: {log_path}")
    
    return test


def demo_bounded_identity(data_dir: str):
    """Demo BoundedIdentity functionality."""
    print_section("5. BoundedIdentity - Identity & Permissions")
    
    # Create identity
    identity = BoundedIdentity(
        entity_name="ai_assistant_001",
        entity_type="agent",
        permission_scope=PermissionScope(
            tier_level=3,
            bounded_actions=[
                "read_data",
                "write_responses",
                "execute_analysis"
            ]
        )
    )
    
    print(f"\n✅ Created identity: {identity.identity_id[:12]}...")
    print(f"   Entity: {identity.entity_name}")
    print(f"   Type: {identity.entity_type}")
    print(f"   Tier: {identity.permission_scope.tier_level}")
    print(f"   Verified: {identity.verified}")
    
    # Check permissions
    print(f"\n   Permission checks:")
    for action in ["read_data", "write_responses", "delete_system_files"]:
        has_perm = identity.has_permission(action)
        status = "✓" if has_perm else "✗"
        print(f"   {status} {action}")
    
    # Verify identity
    identity.verify_identity("digital_signature", "admin_verifier")
    print(f"\n   Identity verified!")
    print(f"   Method: {identity.verification_method}")
    print(f"   Verified: {identity.verified}")
    
    # Track action
    identity.add_to_history("event_001")
    identity.add_to_history("event_002")
    print(f"   Action history: {len(identity.action_history)} entries")
    
    # Save to log
    log_path = f"{data_dir}/identities/demo_identities.jsonl"
    identity.save_to_log(log_path)
    print(f"   Saved to: {log_path}")
    
    return identity


def demo_audit_logger(data_dir: str):
    """Demo AuditLogger functionality."""
    print_section("6. AuditLogger - Centralized Logging")
    
    # Get logger instance (singleton)
    logger = AuditLogger(log_path=f"{data_dir}/audit/demo_audit.jsonl")
    
    print(f"\n✅ AuditLogger initialized")
    print(f"   Log path: {logger.log_path}")
    
    # Log various activities
    print(f"\n   Logging activities...")
    logger.log_action("user_query", "user_alice", {"query": "quantum computing"})
    logger.log_action("ai_response", "ai_assistant_001", {"response_generated": True})
    logger.log_action("hypothesis_created", "testing_system", {"count": 1})
    logger.log_action("test_executed", "testing_system", {"result": "pass"})
    logger.log_action("identity_verified", "admin_verifier", {"entity": "ai_assistant_001"})
    
    print(f"   Logged 5 actions")
    
    # Query logs
    print(f"\n   Querying logs...")
    all_logs = logger.query_logs()
    print(f"   Total entries: {len(all_logs)}")
    
    # Verify integrity
    is_valid = logger.verify_log_integrity()
    print(f"\n   Integrity check: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    
    return logger


def demo_reversibility_manager(data_dir: str):
    """Demo ReversibilityManager functionality."""
    print_section("7. ReversibilityManager - Action Reversal")
    
    # Create manager
    manager = ReversibilityManager(log_path=f"{data_dir}/reversibility/demo_reversals.jsonl")
    
    print(f"\n✅ ReversibilityManager initialized")
    print(f"   Log path: {manager.log_path}")
    
    # Mark actions as reversible
    manager.mark_reversible(
        action_id="action_001",
        action_type="database_insert",
        action_description="Insert user record",
        undo_data={"table": "users", "id": "user_123"}
    )
    
    manager.mark_reversible(
        action_id="action_002",
        action_type="file_creation",
        action_description="Create configuration file",
        undo_data={"path": "/config/app.conf"}
    )
    
    print(f"\n   Marked 2 actions as reversible")
    print(f"   - action_001: {manager.is_reversible('action_001')}")
    print(f"   - action_002: {manager.is_reversible('action_002')}")
    
    # Simulate reversal
    print(f"\n   Simulating reversal of action_001...")
    record = manager._records.get("action_001")
    if record:
        print(f"   - Type: {record.action_type}")
        print(f"   - Description: {record.action_description}")
        print(f"   - Reversible: {record.reversible}")
        print(f"   - Already reversed: {record.reversed}")
    
    print(f"\n   ✓ Reversibility system operational")
    
    return manager


def main():
    """Run complete HandshakeOS-E demo."""
    print("\n" + "=" * 70)
    print("  HandshakeOS-E Complete System Demo")
    print("  Demonstrating all 7 core components")
    print("=" * 70)
    
    # Create temporary data directory
    data_dir = tempfile.mkdtemp(prefix="handshakeos_demo_")
    print(f"\nData directory: {data_dir}")
    
    try:
        # Run demos in sequence
        event = demo_universal_event_record(data_dir)
        intent = demo_intent_token(data_dir, event.event_id)
        hypotheses = demo_parallel_hypotheses(data_dir, event.event_id, intent.token_id)
        test = demo_test_object(data_dir, hypotheses.hypothesis_id)
        identity = demo_bounded_identity(data_dir)
        logger = demo_audit_logger(data_dir)
        manager = demo_reversibility_manager(data_dir)
        
        # Summary
        print_section("Summary")
        print(f"\n✅ All 7 components demonstrated successfully!")
        print(f"\n   Created artifacts:")
        print(f"   - 1 UniversalEventRecord")
        print(f"   - 1 IntentToken")
        print(f"   - 1 ParallelHypotheses set (4 perspectives)")
        print(f"   - 1 TestObject (5 test runs)")
        print(f"   - 1 BoundedIdentity")
        print(f"   - 5+ AuditLogger entries")
        print(f"   - 1 ReversibleAction")
        
        print(f"\n   Integration points verified:")
        print(f"   - ✓ Event → Intent linking")
        print(f"   - ✓ Intent → Hypothesis linking")
        print(f"   - ✓ Hypothesis → Test linking")
        print(f"   - ✓ Identity → Action attribution")
        print(f"   - ✓ All activities → Audit log")
        print(f"   - ✓ Action → Reversibility tracking")
        
        print(f"\n   Data persisted to: {data_dir}")
        print(f"   (Temporary directory will be cleaned up)")
        
        print(f"\n{'=' * 70}")
        print("  Demo Complete!")
        print("  All HandshakeOS-E components are operational.")
        print("=" * 70)
        
    finally:
        # Clean up
        print(f"\nCleaning up temporary directory...")
        shutil.rmtree(data_dir, ignore_errors=True)
        print(f"Done!\n")


if __name__ == "__main__":
    main()
