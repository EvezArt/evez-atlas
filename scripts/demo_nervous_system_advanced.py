#!/usr/bin/env python3
"""
Advanced HandshakeOS-E Nervous System Example

This example demonstrates integration of the nervous system into a
realistic scenario: a service that processes user requests with:
- Pre-action intent declaration
- Post-action readout tracking
- Hypothesis management
- Test validation
- Complete attribution and audit trail

This shows how to wrap existing functionality with the nervous system.
"""

import sys
import random
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mastra.nervous_system import (
    NervousSystem,
    Actor,
    IntentToken,
    EventReadout,
    MixtureVector,
    ModelType,
)


class RequestProcessor:
    """
    Example service that processes user requests.
    
    This demonstrates how to integrate the nervous system into
    an existing service to make it fully auditable.
    """
    
    def __init__(self, ns: NervousSystem, actor: Actor):
        self.ns = ns
        self.actor = actor
        self.processed_count = 0
        self.total_processing_time = 0.0
    
    def process_request(self, request_data: dict) -> dict:
        """
        Process a user request with full nervous system tracking.
        
        This method demonstrates:
        1. Declaring intent before action
        2. Executing the action
        3. Recording the readout
        4. Tracking mixture vectors
        """
        # 1. Declare intent before processing
        intent = IntentToken(
            goal=f"Process {request_data['type']} request",
            constraints=[
                "Must complete within 5 seconds",
                "Must return valid JSON",
                "Must not leak sensitive data"
            ],
            success_metric="Request processed successfully with valid response",
            confidence=0.85
        )
        
        # Record event with intent
        event = self.ns.record_event(
            actor_id=self.actor.id,
            intent=intent,
            metadata={
                "request_id": request_data.get("id"),
                "request_type": request_data.get("type"),
                "timestamp": time.time()
            }
        )
        
        # 2. Execute the actual processing
        start_time = time.time()
        try:
            result = self._do_process(request_data)
            processing_time = time.time() - start_time
            
            # Track metrics
            self.processed_count += 1
            self.total_processing_time += processing_time
            
            # 3. Record successful readout
            readout = EventReadout(
                trigger="user_request",
                result_state={
                    "status": "success",
                    "items_processed": result.get("items", 0),
                    "processing_time_ms": processing_time * 1000
                },
                policy_used="standard_processing_policy",
                payoff=1.0,
                success=True
            )
            
            # Create mixture vector (emergent domain signature)
            mixture = MixtureVector(
                components={
                    "computation": 0.4,
                    "user_interaction": 0.3,
                    "data_access": 0.3
                }
            )
            mixture.normalize()
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Record failure readout
            readout = EventReadout(
                trigger="user_request",
                result_state={
                    "status": "error",
                    "error": str(e),
                    "processing_time_ms": processing_time * 1000
                },
                policy_used="error_handling_policy",
                payoff=0.0,
                success=False
            )
            
            mixture = MixtureVector(
                components={
                    "error_handling": 1.0
                }
            )
            
            raise
        
        finally:
            # Always update event with readout
            self.ns.update_event(
                event_id=event.id,
                readout=readout,
                mixture=mixture
            )
        
        return result
    
    def _do_process(self, request_data: dict) -> dict:
        """Simulate actual processing logic."""
        # Simulate variable processing time
        time.sleep(random.uniform(0.1, 0.3))
        
        request_type = request_data.get("type", "unknown")
        
        if request_type == "query":
            return {
                "items": random.randint(10, 100),
                "type": "query_result"
            }
        elif request_type == "update":
            return {
                "updated": True,
                "type": "update_result"
            }
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    def get_metrics(self) -> dict:
        """Get processing metrics."""
        avg_time = (self.total_processing_time / self.processed_count 
                   if self.processed_count > 0 else 0)
        
        return {
            "total_processed": self.processed_count,
            "average_time_seconds": avg_time,
            "total_time_seconds": self.total_processing_time
        }


def setup_hypotheses(ns: NervousSystem) -> dict:
    """
    Set up hypotheses about the service behavior.
    
    This demonstrates parallel model tracking.
    """
    hypotheses = {}
    
    # ME model: Self-understanding
    hypotheses['me'] = ns.create_hypothesis(
        model_type=ModelType.ME,
        description="I can process requests in under 500ms on average",
        probability=0.75,
        falsifiers=["Average processing time exceeds 500ms over 100 requests"],
        mixture=MixtureVector(components={"performance": 0.9, "reliability": 0.1})
    )
    
    # WE model: System-level understanding
    hypotheses['we'] = ns.create_hypothesis(
        model_type=ModelType.WE,
        description="Our system maintains >99% success rate",
        probability=0.80,
        falsifiers=["Success rate drops below 99%"],
        mixture=MixtureVector(components={"reliability": 0.8, "scalability": 0.2})
    )
    
    # SYSTEM model: Infrastructure understanding
    hypotheses['system'] = ns.create_hypothesis(
        model_type=ModelType.SYSTEM,
        description="Current infrastructure handles 100 req/s without degradation",
        probability=0.70,
        falsifiers=["Response time degrades at 100 req/s"],
        mixture=MixtureVector(components={"infrastructure": 0.7, "capacity": 0.3})
    )
    
    return hypotheses


def create_tests(ns: NervousSystem, hypotheses: dict) -> dict:
    """
    Create tests linked to hypotheses.
    
    This demonstrates test-hypothesis linkage.
    """
    tests = {}
    
    # Test for ME hypothesis
    tests['performance'] = ns.create_test(
        name="test_average_processing_time",
        hypothesis_id=hypotheses['me'].id,
        test_code="""
def test_performance():
    metrics = processor.get_metrics()
    assert metrics['average_time_seconds'] < 0.5
        """,
        metadata={"test_type": "performance", "threshold_ms": 500}
    )
    
    # Test for WE hypothesis
    tests['reliability'] = ns.create_test(
        name="test_success_rate",
        hypothesis_id=hypotheses['we'].id,
        test_code="""
def test_reliability():
    events = ns.query_events(actor_id=actor.id)
    success_count = sum(1 for e in events if e.readout and e.readout.success)
    success_rate = success_count / len(events)
    assert success_rate >= 0.99
        """,
        metadata={"test_type": "reliability", "threshold": 0.99}
    )
    
    return tests


def validate_hypotheses(ns: NervousSystem, processor: RequestProcessor, 
                       hypotheses: dict, tests: dict):
    """
    Validate hypotheses based on observed behavior.
    
    This demonstrates how tests inform hypothesis probabilities.
    """
    # Get metrics
    metrics = processor.get_metrics()
    avg_time_ms = metrics['average_time_seconds'] * 1000
    
    # Test performance hypothesis
    performance_passed = avg_time_ms < 500
    ns.record_test_result(
        test_id=tests['performance'].id,
        passed=performance_passed,
        result={
            "average_time_ms": avg_time_ms,
            "threshold_ms": 500,
            "samples": metrics['total_processed']
        }
    )
    
    # Update hypothesis probability based on test
    if performance_passed:
        ns.update_hypothesis(hypotheses['me'].id, probability=0.90)
        print(f"✓ Performance hypothesis CONFIRMED (avg: {avg_time_ms:.1f}ms < 500ms)")
    else:
        ns.update_hypothesis(hypotheses['me'].id, probability=0.40)
        print(f"✗ Performance hypothesis REJECTED (avg: {avg_time_ms:.1f}ms >= 500ms)")
    
    # Test reliability hypothesis
    events = ns.query_events(actor_id=processor.actor.id)
    success_count = sum(1 for e in events if e.readout and e.readout.success)
    success_rate = success_count / len(events) if events else 0
    
    reliability_passed = success_rate >= 0.99
    ns.record_test_result(
        test_id=tests['reliability'].id,
        passed=reliability_passed,
        result={
            "success_rate": success_rate,
            "success_count": success_count,
            "total_count": len(events)
        }
    )
    
    # Update hypothesis
    if reliability_passed:
        ns.update_hypothesis(hypotheses['we'].id, probability=0.95)
        print(f"✓ Reliability hypothesis CONFIRMED (rate: {success_rate:.2%} >= 99%)")
    else:
        ns.update_hypothesis(hypotheses['we'].id, probability=0.50)
        print(f"✗ Reliability hypothesis REJECTED (rate: {success_rate:.2%} < 99%)")


def demonstrate_audit_trail(ns: NervousSystem, processor: RequestProcessor):
    """
    Demonstrate audit trail capabilities.
    
    This shows attribution and rollback capabilities.
    """
    print("\n" + "="*60)
    print("Audit Trail Demonstration")
    print("="*60)
    
    # Get all events
    events = ns.query_events(actor_id=processor.actor.id)
    print(f"\nTotal events recorded: {len(events)}")
    
    if events:
        # Show attribution for first event
        first_event = events[0]
        attribution = ns.get_attribution(first_event.id)
        
        print(f"\nAttribution for event {first_event.id[:8]}...:")
        print(f"  Actor: {attribution['actor']['name']}")
        print(f"  Type: {attribution['actor']['type']}")
        print(f"  Created: {attribution['created_at'][:19]}")
        print(f"  Version: {attribution['version']}")
        
        # Show audit trail
        trail = ns.get_audit_trail(first_event.id)
        print(f"\nAudit trail versions: {len(trail)}")
        for i, version in enumerate(trail, 1):
            print(f"  Version {i}: {version['updated_at'][:19]}")
        
        print("\n  → All versions preserved for rollback")
    
    # Show system statistics
    stats = ns.get_stats()
    print(f"\nSystem Statistics:")
    print(f"  Total events: {stats['total_events']}")
    print(f"  Total hypotheses: {stats['total_hypotheses']}")
    print(f"  Total tests: {stats['total_tests']}")
    print(f"  Total actors: {stats['total_actors']}")


def main():
    """Run the advanced example."""
    print("="*60)
    print("HandshakeOS-E Nervous System - Advanced Integration Example")
    print("="*60)
    
    # Initialize nervous system
    ns = NervousSystem(Path("data/nervous_system_advanced"))
    
    # Register service actor
    actor = Actor(
        name="RequestProcessor Service",
        type="service",
        permissions={"process_requests", "read_data", "write_data"}
    )
    ns.register_actor(actor)
    print(f"\n✓ Registered actor: {actor.name}")
    
    # Create service
    processor = RequestProcessor(ns, actor)
    print(f"✓ Created service with nervous system integration")
    
    # Set up hypotheses
    print("\n" + "="*60)
    print("Setting Up Hypotheses")
    print("="*60)
    
    hypotheses = setup_hypotheses(ns)
    for key, hyp in hypotheses.items():
        print(f"\n{key.upper()} model:")
        print(f"  {hyp.description}")
        print(f"  Initial probability: {hyp.probability}")
    
    # Create tests
    print("\n" + "="*60)
    print("Creating Tests")
    print("="*60)
    
    tests = create_tests(ns, hypotheses)
    print(f"\n✓ Created {len(tests)} tests linked to hypotheses")
    
    # Process sample requests
    print("\n" + "="*60)
    print("Processing Requests")
    print("="*60)
    
    sample_requests = [
        {"id": "req-1", "type": "query"},
        {"id": "req-2", "type": "query"},
        {"id": "req-3", "type": "update"},
        {"id": "req-4", "type": "query"},
        {"id": "req-5", "type": "update"},
    ]
    
    print(f"\nProcessing {len(sample_requests)} requests...")
    for i, request in enumerate(sample_requests, 1):
        result = processor.process_request(request)
        print(f"  {i}. {request['type']}: {result['type']}")
    
    # Get metrics
    metrics = processor.get_metrics()
    print(f"\nMetrics:")
    print(f"  Total processed: {metrics['total_processed']}")
    print(f"  Average time: {metrics['average_time_seconds']*1000:.1f}ms")
    
    # Validate hypotheses
    print("\n" + "="*60)
    print("Validating Hypotheses")
    print("="*60)
    print()
    
    validate_hypotheses(ns, processor, hypotheses, tests)
    
    # Show audit trail
    demonstrate_audit_trail(ns, processor)
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    stats = ns.get_stats()
    print(f"\nGenerated:")
    print(f"  • {stats['total_events']} events (fully auditable)")
    print(f"  • {stats['total_hypotheses']} hypotheses (parallel models)")
    print(f"  • {stats['total_tests']} tests (linked to hypotheses)")
    print(f"  • {stats['total_actors']} actors (full attribution)")
    
    print(f"\nAll data stored in: {ns.data_dir}")
    
    print("\nKey principles demonstrated:")
    print("  ✓ Intent declaration before action")
    print("  ✓ Readout recording after action")
    print("  ✓ Mixture vectors for domain signatures")
    print("  ✓ Parallel hypothesis tracking")
    print("  ✓ Test-hypothesis linkage")
    print("  ✓ Complete attribution and audit trail")
    print("  ✓ Rollback capability via versioning")
    
    print("\n" + "="*60)
    print("Integration complete! Service is now fully auditable.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
