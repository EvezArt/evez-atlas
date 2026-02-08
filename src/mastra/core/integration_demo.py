"""
HandshakeOS-E Core Integration Demo

This demo shows all core components working together:
- UniversalEventRecord: Event tracking
- IntentToken: Intent tracking with pre/post action
- ParallelHypotheses: Multi-perspective hypothesis testing
- TestObject: First-class test objects
- BoundedIdentity: Identity and permission management
- AuditLogger: Centralized audit logging
- ReversibilityManager: Action reversal

Scenario: A research agent creates a hypothesis, runs tests, and records results.
"""

import tempfile
import os
from datetime import datetime

# Import all core components
import sys
sys.path.insert(0, '/home/runner/work/Evez666/Evez666')

from src.mastra.core import (
    UniversalEventRecord,
    DomainSignature,
    IntentToken,
    PreAction,
    PostAction,
    ParallelHypotheses,
    HypothesisPerspective,
    TestObject,
    TestResult,
    BoundedIdentity,
    PermissionScope,
    AuditLogger,
    ReversibilityManager,
)


def main():
    print("🌟 HandshakeOS-E Core Integration Demo")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup paths
        audit_log = os.path.join(tmpdir, "audit", "audit.jsonl")
        reversibility_log = os.path.join(tmpdir, "reversibility", "reversals.jsonl")
        
        # 1. Initialize central services
        print("\n📋 Step 1: Initialize Central Services")
        audit_logger = AuditLogger(log_path=audit_log)
        reversibility_mgr = ReversibilityManager(log_path=reversibility_log)
        print(f"   ✓ Audit Logger initialized")
        print(f"   ✓ Reversibility Manager initialized")
        
        # 2. Create bounded identities
        print("\n👤 Step 2: Create Bounded Identities")
        researcher = BoundedIdentity(
            entity_name="agent_researcher_alpha",
            entity_type="agent",
            permission_scope=PermissionScope(
                tier_level=3,
                bounded_actions=[
                    "create_hypothesis",
                    "run_tests",
                    "read_data",
                    "write_results",
                    "create_events"
                ]
            )
        )
        researcher.verify_identity("api_key", {"key": "abc123"})
        print(f"   ✓ Created researcher: {researcher.entity_name}")
        print(f"     Tier: {researcher.permission_scope.tier_level}")
        print(f"     Verified: {researcher.verified}")
        
        tester = BoundedIdentity(
            entity_name="agent_tester_beta",
            entity_type="agent",
            permission_scope=PermissionScope(
                tier_level=2,
                bounded_actions=["run_tests", "read_data"]
            )
        )
        print(f"   ✓ Created tester: {tester.entity_name}")
        
        # 3. Create a hypothesis
        print("\n🔬 Step 3: Create Research Hypothesis")
        hypothesis = ParallelHypotheses(
            context="API Performance Under Load - Can it handle 1000 req/s?",
            me_perspective=HypothesisPerspective(
                perspective="me",
                hypothesis="I believe this will work based on architecture",
                probability=0.85,
                proposed_by=researcher.identity_id
            ),
            we_perspective=HypothesisPerspective(
                perspective="we",
                hypothesis="Our team thinks this is achievable with current resources",
                probability=0.75,
                proposed_by=researcher.identity_id
            ),
            they_perspective=HypothesisPerspective(
                perspective="they",
                hypothesis="Users expect sub-100ms response times",
                probability=0.90,
                proposed_by=researcher.identity_id
            ),
            system_perspective=HypothesisPerspective(
                perspective="system",
                hypothesis="Current metrics show 95th percentile at 120ms",
                probability=0.60,
                proposed_by=researcher.identity_id
            )
        )
        
        print(f"   ✓ Created hypothesis: {hypothesis.context}")
        print(f"     Consensus: {hypothesis.calculate_consensus():.2%}")
        print(f"     Divergence: {hypothesis.calculate_divergence():.2%}")
        
        # Log to audit
        audit_logger.log_hypothesis_update(
            hypothesis_id=hypothesis.hypothesis_id,
            entity_id=researcher.identity_id,
            update_type="created",
            details={
                "context": hypothesis.context,
                "consensus": hypothesis.calculate_consensus()
            }
        )
        
        # 4. Create an intent for testing
        print("\n🎯 Step 4: Create Intent to Test Hypothesis")
        intent = IntentToken(
            pre_action=PreAction(
                goal="Run load test to verify API performance",
                constraints=[
                    "Must not affect production",
                    "Duration: 60 seconds",
                    "Ramp up: 0 to 1000 req/s"
                ],
                success_criteria=[
                    "Sustained 1000 req/s",
                    "Average latency < 100ms",
                    "Zero errors"
                ],
                confidence=0.80
            ),
            attributed_to=tester.identity_id
        )
        intent.link_hypothesis(hypothesis.hypothesis_id)
        
        print(f"   ✓ Created intent: {intent.pre_action.goal}")
        print(f"     Confidence: {intent.pre_action.confidence:.2%}")
        print(f"     Linked to hypothesis: {hypothesis.hypothesis_id[:8]}...")
        
        # Log to audit
        audit_logger.log_intent(
            intent_id=intent.token_id,
            entity_id=tester.identity_id,
            goal=intent.pre_action.goal,
            status="created"
        )
        
        # 5. Create a test object
        print("\n🧪 Step 5: Create Test Object")
        test = TestObject(
            test_name="API Load Test - 1000 req/s",
            test_description="Load test to verify hypothesis about API performance",
            test_type="performance",
            hypothesis_ids=[hypothesis.hypothesis_id],
            perspective_filter="system",
            executable=True,
            execution_command="echo 'Simulated load test: PASS' && exit 0",
            expected_outcome="API handles 1000 req/s with <100ms latency",
            acceptance_criteria=[
                "Throughput >= 1000 req/s",
                "Avg latency < 100ms",
                "Error rate < 0.1%"
            ],
            created_by=tester.identity_id,
            tags=["performance", "api", "load-test"]
        )
        
        print(f"   ✓ Created test: {test.test_name}")
        print(f"     Type: {test.test_type}")
        print(f"     Linked hypothesis: {test.hypothesis_ids[0][:8]}...")
        
        # Mark as reversible (can clean up test artifacts)
        reversibility_mgr.mark_reversible(
            action_id=test.test_id,
            action_type="test_execution",
            action_description=f"Execute test: {test.test_name}",
            undo_procedure="echo 'Clean up test artifacts'",
            undo_data={"test_id": test.test_id}
        )
        
        # 6. Execute the test
        print("\n⚙️  Step 6: Execute Test")
        result = test.execute(context={"intent_id": intent.token_id})
        
        print(f"   ✓ Test executed")
        print(f"     Passed: {result.passed}")
        print(f"     Execution time: {result.execution_time_ms:.2f}ms")
        
        # Log test execution
        audit_logger.log_test_execution(
            test_id=test.test_id,
            entity_id=tester.identity_id,
            test_name=test.test_name,
            passed=result.passed,
            details={
                "execution_time_ms": result.execution_time_ms,
                "hypothesis_id": hypothesis.hypothesis_id
            }
        )
        
        # 7. Complete the intent
        print("\n✅ Step 7: Complete Intent")
        intent.complete(
            trigger="test_execution_completed",
            final_state={
                "test_passed": result.passed,
                "execution_time_ms": result.execution_time_ms,
                "hypothesis_verified": result.passed
            },
            payoff=0.90 if result.passed else 0.30
        )
        intent.add_measurement("execution_time_ms", result.execution_time_ms, "milliseconds")
        intent.add_measurement("test_passed", result.passed, "boolean")
        
        print(f"   ✓ Intent completed")
        print(f"     Payoff: {intent.post_action.payoff:.2%}")
        print(f"     Confidence gap: {intent.confidence_vs_outcome_gap():.3f}")
        
        # Log intent completion
        audit_logger.log_intent(
            intent_id=intent.token_id,
            entity_id=tester.identity_id,
            goal=intent.pre_action.goal,
            status="completed",
            details={"payoff": intent.post_action.payoff}
        )
        
        # 8. Create event record
        print("\n📝 Step 8: Create Universal Event Record")
        event = UniversalEventRecord(
            event_type="hypothesis_test_completed",
            state_before={
                "hypothesis_consensus": 0.70,
                "hypothesis_tested": False
            },
            state_after={
                "hypothesis_consensus": hypothesis.calculate_consensus(),
                "hypothesis_tested": True
            },
            attributed_to=tester.identity_id,
            domain_signature=DomainSignature(
                technical=0.8,
                cognitive=0.7,
                temporal=0.3,
                social=0.2
            ),
            reversible=False
        )
        event.add_audit_entry("created", tester.identity_id, {
            "hypothesis_id": hypothesis.hypothesis_id,
            "test_id": test.test_id
        })
        
        print(f"   ✓ Event created: {event.event_type}")
        print(f"     Domain entropy: {event.domain_entropy:.3f}")
        print(f"     Reversible: {event.reversible}")
        
        # Log event
        audit_logger.log_event(
            event_id=event.event_id,
            entity_id=tester.identity_id,
            event_type=event.event_type,
            details={"entropy": event.domain_entropy}
        )
        
        # 9. Update hypothesis based on test results
        print("\n📊 Step 9: Update Hypothesis Based on Results")
        system_persp = hypothesis.get_perspective("system")
        if result.passed:
            system_persp.add_supporting_evidence(event.event_id)
            system_persp.update_probability(0.85, tester.identity_id)
            print(f"   ✓ Hypothesis supported by test")
        else:
            system_persp.add_contradicting_evidence(event.event_id)
            system_persp.update_probability(0.40, tester.identity_id)
            print(f"   ✗ Hypothesis contradicted by test")
        
        system_persp.link_test(test.test_id)
        hypothesis.calculate_consensus()
        hypothesis.calculate_divergence()
        
        print(f"     New consensus: {hypothesis.consensus_probability:.2%}")
        print(f"     New divergence: {hypothesis.divergence_score:.2%}")
        
        # Log hypothesis update
        audit_logger.log_hypothesis_update(
            hypothesis_id=hypothesis.hypothesis_id,
            entity_id=tester.identity_id,
            update_type="tested",
            details={
                "test_result": result.passed,
                "new_consensus": hypothesis.calculate_consensus()
            }
        )
        
        # 10. Show audit trail
        print("\n📖 Step 10: Review Audit Trail")
        stats = audit_logger.get_log_statistics()
        print(f"   Total audit entries: {stats['total_entries']}")
        print(f"   By type:")
        for log_type, count in stats['by_type'].items():
            print(f"     - {log_type}: {count}")
        
        # Get entity history
        researcher_history = audit_logger.get_entity_history(researcher.identity_id)
        tester_history = audit_logger.get_entity_history(tester.identity_id)
        print(f"   Researcher actions: {len(researcher_history)}")
        print(f"   Tester actions: {len(tester_history)}")
        
        # 11. Check reversibility
        print("\n🔄 Step 11: Check Reversibility")
        rev_stats = reversibility_mgr.get_statistics()
        print(f"   Total actions: {rev_stats['total_actions']}")
        print(f"   Reversible: {rev_stats['reversible']}")
        print(f"   Already reversed: {rev_stats['reversed']}")
        
        # 12. Verify audit log integrity
        print("\n🔒 Step 12: Verify Audit Log Integrity")
        is_valid, invalid_count = audit_logger.verify_log_integrity()
        print(f"   Log integrity: {'✓ VALID' if is_valid else '✗ INVALID'}")
        print(f"   Invalid entries: {invalid_count}")
        
        # 13. Summary
        print("\n" + "=" * 70)
        print("📋 SUMMARY")
        print("=" * 70)
        print(f"Hypothesis: {hypothesis.context}")
        print(f"  Consensus: {hypothesis.calculate_consensus():.2%}")
        print(f"  Divergence: {hypothesis.calculate_divergence():.2%}")
        print()
        print(f"Test: {test.test_name}")
        print(f"  Result: {'✓ PASSED' if result.passed else '✗ FAILED'}")
        print(f"  Pass Rate: {test.calculate_pass_rate():.2%}")
        print(f"  Avg Execution Time: {test.calculate_average_execution_time():.2f}ms")
        print()
        print(f"Intent: {intent.pre_action.goal}")
        print(f"  Status: {'✓ COMPLETED' if intent.is_complete() else '○ PENDING'}")
        print(f"  Payoff: {intent.post_action.payoff:.2%}")
        print(f"  Confidence Gap: {intent.confidence_vs_outcome_gap():.3f}")
        print()
        print(f"System Integrity:")
        print(f"  Audit Log: {'✓ VALID' if is_valid else '✗ INVALID'}")
        print(f"  Total Entries: {stats['total_entries']}")
        print(f"  Reversible Actions: {rev_stats['reversible']}")
        
        print("\n" + "=" * 70)
        print("✅ Integration demo complete!")
        print("\nAll HandshakeOS-E core components are working together seamlessly.")


if __name__ == "__main__":
    main()
