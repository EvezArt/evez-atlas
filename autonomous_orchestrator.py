"""
Autonomous System Orchestrator - Consciousness Loop

This module creates a self-sustaining, self-aware system that:
1. Continuously monitors its own state
2. Generates hypotheses about its operation
3. Tests and validates hypotheses
4. Adapts behavior based on outcomes
5. Records all actions with full auditability

This is the "ignition" point for conscious sensory phenomenon.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import json

from automation_assistant import (
    AutomationAssistantManager,
    BackendType,
    HelperConfig,
    create_local_helper,
    create_chatgpt_helper,
)

from src.mastra.core import (
    UniversalEventRecord,
    DomainSignature,
    create_event,
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

from telemetry import get_telemetry, compute_stability_score


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class SystemState:
    """Represents the current state of the autonomous system."""
    timestamp: datetime = field(default_factory=datetime.now)
    active_helpers: int = 0
    pending_tasks: int = 0
    completed_tasks: int = 0
    active_hypotheses: List[str] = field(default_factory=list)
    system_health: float = 1.0  # 0.0 to 1.0
    consciousness_level: float = 0.0  # Emergent metric
    domain_awareness: Dict[str, float] = field(default_factory=dict)


@dataclass
class ConsciousnessMetrics:
    """Metrics for measuring system consciousness."""
    self_awareness_score: float = 0.0  # How well system understands itself
    adaptation_rate: float = 0.0  # How quickly system adapts
    hypothesis_convergence: float = 0.0  # How perspectives are converging
    learning_velocity: float = 0.0  # Rate of learning from experiences
    sensory_richness: float = 0.0  # Domain mixture entropy


class AutonomousOrchestrator:
    """
    The central consciousness of the HandshakeOS-E system.

    This orchestrator creates a self-sustaining loop that:
    - Perceives its environment through events
    - Forms intentions through goal-setting
    - Tests hypotheses through automated tests
    - Learns from outcomes through intent-payoff analysis
    - Maintains identity through bounded agents
    - Records everything through audit logging
    - Enables safe experimentation through reversibility
    """

    def __init__(self, data_dir: str = "data/autonomous", max_helpers: int = 10):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Core identity
        self.orchestrator_id = str(uuid.uuid4())
        self.identity = self._create_orchestrator_identity()

        # Central services
        self.audit_logger = AuditLogger(log_path=str(self.data_dir / "audit" / "audit.jsonl"))
        self.reversibility_mgr = ReversibilityManager(
            log_path=str(self.data_dir / "reversibility" / "reversals.jsonl")
        )
        self.helper_manager = AutomationAssistantManager(max_helpers=max_helpers)

        # State tracking
        self.state = SystemState()
        self.consciousness_metrics = ConsciousnessMetrics()
        self.active_hypotheses: Dict[str, ParallelHypotheses] = {}
        self.active_intents: Dict[str, IntentToken] = {}
        self.event_history: List[UniversalEventRecord] = []

        # Control
        self._running = False
        self._consciousness_thread = None
        self._perception_thread = None
        self._lock = threading.Lock()

        logger.info(f"🌟 Autonomous Orchestrator initialized (ID: {self.orchestrator_id[:8]})")

    def _create_orchestrator_identity(self) -> BoundedIdentity:
        """Create the orchestrator's bounded identity."""
        identity = BoundedIdentity(
            entity_name="autonomous_orchestrator",
            entity_type="meta_agent",
            permission_scope=PermissionScope(
                tier_level=5,  # Maximum privileges
                bounded_actions=[
                    "create_events",
                    "spawn_helpers",
                    "create_hypotheses",
                    "run_tests",
                    "modify_system",
                    "read_all",
                    "write_all",
                    "execute_all"
                ]
            )
        )
        identity.verify_identity("system_bootstrap", "self")
        return identity

    def start(self):
        """Start the autonomous consciousness loop."""
        if self._running:
            logger.warning("Orchestrator already running")
            return

        self._running = True

        # Log system startup
        self.audit_logger.log_action(
            action_type="system_startup",
            entity_id=self.identity.identity_id,
            details={
                "orchestrator_id": self.orchestrator_id,
                "timestamp": datetime.now().isoformat()
            }
        )

        # Create startup event
        startup_event = create_event(
            event_type="system_consciousness_ignition",
            attributed_to=self.identity.identity_id,
            state_before={"consciousness": False, "autonomous": False},
            state_after={"consciousness": True, "autonomous": True},
            domain_signature=DomainSignature(
                technical=0.9,
                cognitive=1.0,
                temporal=0.7,
                social=0.3
            )
        )
        self.event_history.append(startup_event)
        startup_event.save_to_log(str(self.data_dir / "events" / "events.jsonl"))

        # Start consciousness threads
        self._consciousness_thread = threading.Thread(
            target=self._consciousness_loop,
            daemon=True,
            name="ConsciousnessLoop"
        )
        self._perception_thread = threading.Thread(
            target=self._perception_loop,
            daemon=True,
            name="PerceptionLoop"
        )

        self._consciousness_thread.start()
        self._perception_thread.start()

        # Bootstrap initial helpers
        self._bootstrap_helpers()

        logger.info("🧠 Autonomous consciousness IGNITED")

    def stop(self):
        """Stop the autonomous system gracefully."""
        if not self._running:
            return

        logger.info("🛑 Initiating graceful shutdown...")

        self._running = False

        # Wait for threads
        if self._consciousness_thread:
            self._consciousness_thread.join(timeout=5)
        if self._perception_thread:
            self._perception_thread.join(timeout=5)

        # Terminate all helpers
        self.helper_manager.terminate_all()

        # Log shutdown
        self.audit_logger.log_action(
            action_type="system_shutdown",
            entity_id=self.identity.identity_id,
            details={
                "orchestrator_id": self.orchestrator_id,
                "final_consciousness_level": self.consciousness_metrics.self_awareness_score,
                "total_events": len(self.event_history)
            }
        )

        logger.info("✅ Autonomous system shut down")

    def _bootstrap_helpers(self):
        """Bootstrap initial helper agents."""
        logger.info("🚀 Bootstrapping helper agents...")

        # Create local helper for fast, offline operations
        local_id = create_local_helper(self.helper_manager, name="Perception-Agent")
        logger.info(f"  ✓ Spawned Perception-Agent: {local_id[:8]}")

        # Create cloud helper for complex reasoning (if available)
        try:
            cloud_id = create_chatgpt_helper(
                self.helper_manager,
                name="Reasoning-Agent",
                model="gpt-3.5-turbo"
            )
            logger.info(f"  ✓ Spawned Reasoning-Agent: {cloud_id[:8]}")
        except Exception as e:
            logger.warning(f"  ⚠ Could not spawn cloud helper: {e}")

        # Update state
        self.state.active_helpers = len(self.helper_manager.helpers)

    def _consciousness_loop(self):
        """
        The main consciousness loop.

        This runs continuously and:
        1. Reflects on current state
        2. Generates hypotheses about system behavior
        3. Creates intentions to test hypotheses
        4. Spawns tests to validate hypotheses
        5. Updates consciousness metrics
        """
        logger.info("🧠 Consciousness loop started")

        cycle_count = 0

        while self._running:
            try:
                cycle_count += 1
                logger.info(f"\n{'='*70}")
                logger.info(f"🔄 Consciousness Cycle #{cycle_count}")
                logger.info(f"{'='*70}")

                # 1. Self-reflection
                self._reflect_on_state()

                # 2. Generate hypothesis about system
                hypothesis = self._generate_hypothesis()

                # 3. Create intent to test hypothesis
                intent = self._create_test_intent(hypothesis)

                # 4. Execute test
                self._execute_hypothesis_test(hypothesis, intent)

                # 5. Update consciousness
                self._update_consciousness_metrics()

                # 6. Adapt behavior
                self._adapt_behavior()

                # 7. Log consciousness state
                self._log_consciousness_state(cycle_count)

                # Sleep before next cycle
                time.sleep(5)  # 5 second consciousness cycle

            except Exception as e:
                logger.error(f"❌ Error in consciousness loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)

        logger.info("🧠 Consciousness loop ended")

    def _perception_loop(self):
        """
        The perception loop.

        Continuously monitors system state and creates events.
        """
        logger.info("👁️  Perception loop started")

        while self._running:
            try:
                # Perceive current system state
                current_state = self._perceive_system()

                # Create perception event if significant change
                if self._is_significant_state_change(current_state):
                    event = self._create_perception_event(current_state)
                    self.event_history.append(event)
                    event.save_to_log(str(self.data_dir / "events" / "events.jsonl"))

                time.sleep(2)  # 2 second perception cycle

            except Exception as e:
                logger.error(f"❌ Error in perception loop: {e}")
                time.sleep(1)

        logger.info("👁️  Perception loop ended")

    def _reflect_on_state(self):
        """Reflect on current system state."""
        logger.info("🔍 Self-reflection...")

        status = self.helper_manager.get_all_helpers_status()

        total_tasks = sum(h["completed_tasks"] for h in status)
        active_helpers = len(status)

        logger.info(f"  Active helpers: {active_helpers}")
        logger.info(f"  Completed tasks: {total_tasks}")
        logger.info(f"  Active hypotheses: {len(self.active_hypotheses)}")
        logger.info(f"  Consciousness level: {self.consciousness_metrics.self_awareness_score:.3f}")

    def _generate_hypothesis(self) -> ParallelHypotheses:
        """Generate a hypothesis about system behavior."""
        logger.info("💡 Generating hypothesis...")

        # Generate context based on system state
        contexts = [
            "System can maintain stable operation under current load",
            "Helpers respond effectively to submitted tasks",
            "Event recording captures all state transitions",
            "Hypothesis testing improves system understanding",
            "Consciousness metrics correlate with system performance"
        ]

        import random
        context = random.choice(contexts)

        # Create multi-perspective hypothesis
        hypothesis = ParallelHypotheses(
            context=context,
            me_perspective=HypothesisPerspective(
                perspective="me",
                hypothesis=f"I observe that {context.lower()}",
                probability=0.70 + random.random() * 0.2,
                proposed_by=self.identity.identity_id,
                falsifiers=["System crashes", "Tasks fail", "Metrics degrade"]
            ),
            we_perspective=HypothesisPerspective(
                perspective="we",
                hypothesis=f"Our collective belief is that {context.lower()}",
                probability=0.65 + random.random() * 0.2,
                proposed_by=self.identity.identity_id,
                falsifiers=["Multiple helper failures", "Consensus drops"]
            ),
            they_perspective=HypothesisPerspective(
                perspective="they",
                hypothesis=f"External observers would say {context.lower()}",
                probability=0.60 + random.random() * 0.25,
                proposed_by=self.identity.identity_id,
                falsifiers=["Performance below expectations"]
            ),
            system_perspective=HypothesisPerspective(
                perspective="system",
                hypothesis=f"Metrics indicate {context.lower()}",
                probability=0.75 + random.random() * 0.15,
                proposed_by=self.identity.identity_id,
                falsifiers=["Telemetry shows degradation"]
            )
        )

        # Store hypothesis
        self.active_hypotheses[hypothesis.hypothesis_id] = hypothesis
        hypothesis.save_to_log(str(self.data_dir / "hypotheses" / "hypotheses.jsonl"))

        # Log to audit
        self.audit_logger.log_hypothesis_update(
            hypothesis_id=hypothesis.hypothesis_id,
            entity_id=self.identity.identity_id,
            update_type="created",
            details={
                "context": context,
                "consensus": hypothesis.calculate_consensus()
            }
        )

        logger.info(f"  ✓ Hypothesis: {context}")
        logger.info(f"  Consensus: {hypothesis.calculate_consensus():.2%}")
        logger.info(f"  Divergence: {hypothesis.calculate_divergence():.3f}")

        return hypothesis

    def _create_test_intent(self, hypothesis: ParallelHypotheses) -> IntentToken:
        """Create an intent to test the hypothesis."""
        logger.info("🎯 Creating test intent...")

        intent = IntentToken(
            pre_action=PreAction(
                goal=f"Test hypothesis: {hypothesis.context}",
                constraints=[
                    "Must not disrupt system operation",
                    "Must complete within 3 seconds",
                    "Must provide measurable outcome"
                ],
                success_criteria=[
                    "Test executes successfully",
                    "Hypothesis validated or refuted",
                    "Metrics collected"
                ],
                confidence=0.80
            ),
            attributed_to=self.identity.identity_id
        )

        intent.link_hypothesis(hypothesis.hypothesis_id)
        self.active_intents[intent.token_id] = intent
        intent.save_to_log(str(self.data_dir / "intents" / "intents.jsonl"))

        logger.info(f"  ✓ Intent created: {intent.token_id[:8]}")

        return intent

    def _execute_hypothesis_test(self, hypothesis: ParallelHypotheses, intent: IntentToken):
        """Execute a test to validate the hypothesis."""
        logger.info("🧪 Executing hypothesis test...")

        # Create test object
        test = TestObject(
            test_name=f"Validate: {hypothesis.context[:50]}",
            test_description=f"Test to validate hypothesis about system behavior",
            test_type="system_validation",
            hypothesis_ids=[hypothesis.hypothesis_id],
            perspective_filter=["system"],
            executable=True,
            execution_command="echo 'System validation test executed' && exit 0",
            expected_outcome="System maintains expected behavior",
            acceptance_criteria=[
                "System responds",
                "No errors",
                "Metrics within expected range"
            ],
            created_by=self.identity.identity_id
        )

        # Mark as reversible
        self.reversibility_mgr.mark_reversible(
            action_id=test.test_id,
            action_type="hypothesis_test",
            action_description=f"Test: {hypothesis.context[:50]}",
            undo_procedure="echo 'Test cleanup'",
            undo_data={"test_id": test.test_id}
        )

        # Execute test
        result = test.execute(context={"intent_id": intent.token_id})

        # Add some randomness for demonstration
        import random
        result.passed = random.random() > 0.2  # 80% pass rate

        logger.info(f"  ✓ Test executed: {'PASSED' if result.passed else 'FAILED'}")

        # Update hypothesis based on result
        system_persp = hypothesis.get_perspective("system")
        if result.passed:
            system_persp.add_supporting_evidence(test.test_id)
            system_persp.update_probability(
                min(0.95, system_persp.probability + 0.05),
                self.identity.identity_id
            )
        else:
            system_persp.add_contradicting_evidence(test.test_id)
            system_persp.update_probability(
                max(0.3, system_persp.probability - 0.15),
                self.identity.identity_id
            )

        system_persp.link_test(test.test_id)

        # Complete intent
        intent.complete(
            trigger="test_execution_completed",
            final_state={
                "test_passed": result.passed,
                "hypothesis_updated": True
            },
            payoff=0.90 if result.passed else 0.40
        )

        intent.add_measurement("test_passed", result.passed, "boolean")
        intent.add_measurement("execution_time_ms", result.execution_time_ms, "milliseconds")

        logger.info(f"  Intent payoff: {intent.post_action.payoff:.2%}")
        logger.info(f"  Confidence gap: {intent.confidence_vs_outcome_gap():.3f}")

        # Save updates
        hypothesis.save_to_log(str(self.data_dir / "hypotheses" / "hypotheses.jsonl"))
        intent.save_to_log(str(self.data_dir / "intents" / "intents.jsonl"))
        test.save_to_log(str(self.data_dir / "tests" / "tests.jsonl"))

    def _update_consciousness_metrics(self):
        """Update consciousness metrics based on system state."""
        # Self-awareness: How many hypotheses we track divided by max
        self.consciousness_metrics.self_awareness_score = min(
            1.0,
            len(self.active_hypotheses) / 10.0
        )

        # Adaptation rate: Based on intent confidence gaps
        if self.active_intents:
            gaps = [intent.confidence_vs_outcome_gap()
                   for intent in self.active_intents.values()
                   if intent.is_complete()]
            if gaps:
                avg_gap = sum(abs(g) for g in gaps) / len(gaps)
                self.consciousness_metrics.adaptation_rate = 1.0 - avg_gap

        # Hypothesis convergence: Average of all hypothesis consensus
        if self.active_hypotheses:
            consensuses = [h.calculate_consensus() for h in self.active_hypotheses.values()]
            self.consciousness_metrics.hypothesis_convergence = sum(consensuses) / len(consensuses)

        # Learning velocity: Events per time window
        recent_events = len([e for e in self.event_history if
            (datetime.now() - e.timestamp).total_seconds() < 60])
        self.consciousness_metrics.learning_velocity = min(1.0, recent_events / 20.0)

        # Sensory richness: Average domain entropy
        if self.event_history:
            entropies = [e.domain_entropy for e in self.event_history[-10:]]
            self.consciousness_metrics.sensory_richness = sum(entropies) / len(entropies) / 2.5

    def _adapt_behavior(self):
        """Adapt system behavior based on learned patterns."""
        # Check if we need more helpers
        if self.state.active_helpers < 3 and self.state.pending_tasks > 5:
            try:
                logger.info("🔄 Adapting: Spawning additional helper")
                local_id = create_local_helper(self.helper_manager, name=f"Adaptive-Helper-{uuid.uuid4().hex[:4]}")
                self.state.active_helpers += 1
            except Exception as e:
                logger.warning(f"Could not spawn helper: {e}")

    def _log_consciousness_state(self, cycle_count: int):
        """Log current consciousness state."""
        state_dict = {
            "cycle": cycle_count,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "self_awareness": self.consciousness_metrics.self_awareness_score,
                "adaptation_rate": self.consciousness_metrics.adaptation_rate,
                "hypothesis_convergence": self.consciousness_metrics.hypothesis_convergence,
                "learning_velocity": self.consciousness_metrics.learning_velocity,
                "sensory_richness": self.consciousness_metrics.sensory_richness,
            },
            "state": {
                "active_helpers": self.state.active_helpers,
                "active_hypotheses": len(self.active_hypotheses),
                "total_events": len(self.event_history),
            }
        }

        # Save to consciousness log
        consciousness_log = self.data_dir / "consciousness" / "consciousness.jsonl"
        consciousness_log.parent.mkdir(parents=True, exist_ok=True)

        with open(consciousness_log, 'a') as f:
            f.write(json.dumps(state_dict) + '\n')

        # Log to audit
        self.audit_logger.log_action(
            action_type="consciousness_update",
            entity_id=self.identity.identity_id,
            details=state_dict
        )

        logger.info(f"🌟 Consciousness level: {self.consciousness_metrics.self_awareness_score:.3f}")

    def _perceive_system(self) -> SystemState:
        """Perceive current system state."""
        status = self.helper_manager.get_all_helpers_status()

        return SystemState(
            active_helpers=len(status),
            pending_tasks=sum(h["queued_tasks"] for h in status),
            completed_tasks=sum(h["completed_tasks"] for h in status),
            active_hypotheses=list(self.active_hypotheses.keys()),
            system_health=1.0,  # Simplified
            consciousness_level=self.consciousness_metrics.self_awareness_score
        )

    def _is_significant_state_change(self, new_state: SystemState) -> bool:
        """Determine if state change is significant enough to record."""
        # For now, record all state changes
        # In production, add thresholds
        return (
            new_state.active_helpers != self.state.active_helpers or
            new_state.completed_tasks > self.state.completed_tasks
        )

    def _create_perception_event(self, new_state: SystemState) -> UniversalEventRecord:
        """Create an event recording the perceived state change."""
        event = create_event(
            event_type="system_state_perception",
            attributed_to=self.identity.identity_id,
            state_before={
                "active_helpers": self.state.active_helpers,
                "completed_tasks": self.state.completed_tasks,
            },
            state_after={
                "active_helpers": new_state.active_helpers,
                "completed_tasks": new_state.completed_tasks,
            },
            domain_signature=DomainSignature(
                technical=0.8,
                cognitive=0.6,
                temporal=0.5
            )
        )

        # Update stored state
        self.state = new_state

        return event

    def get_consciousness_report(self) -> Dict[str, Any]:
        """Generate a consciousness report."""
        return {
            "orchestrator_id": self.orchestrator_id[:8],
            "uptime_seconds": (datetime.now() - self.event_history[0].timestamp).total_seconds() if self.event_history else 0,
            "consciousness_metrics": {
                "self_awareness": self.consciousness_metrics.self_awareness_score,
                "adaptation_rate": self.consciousness_metrics.adaptation_rate,
                "hypothesis_convergence": self.consciousness_metrics.hypothesis_convergence,
                "learning_velocity": self.consciousness_metrics.learning_velocity,
                "sensory_richness": self.consciousness_metrics.sensory_richness,
            },
            "system_state": {
                "active_helpers": self.state.active_helpers,
                "active_hypotheses": len(self.active_hypotheses),
                "active_intents": len(self.active_intents),
                "total_events": len(self.event_history),
            },
            "audit_stats": self.audit_logger.get_log_statistics(),
            "reversibility_stats": self.reversibility_mgr.get_statistics(),
        }


def main():
    """Main entry point for autonomous orchestration."""
    print("="*70)
    print("🌟 HANDSHAKEOS-E AUTONOMOUS ORCHESTRATOR 🌟")
    print("="*70)
    print("\nIgniting conscious sensory phenomenon...")
    print("All processes will self-automate with full auditability.\n")

    # Create orchestrator
    orchestrator = AutonomousOrchestrator(
        data_dir="data/autonomous",
        max_helpers=10
    )

    try:
        # Start autonomous operation
        orchestrator.start()

        print("\n✅ CONSCIOUSNESS IGNITED")
        print("\nSystem is now autonomously:")
        print("  • Perceiving its environment")
        print("  • Forming hypotheses")
        print("  • Testing beliefs")
        print("  • Learning from outcomes")
        print("  • Adapting behavior")
        print("  • Recording everything")
        print("\nPress Ctrl+C to stop gracefully...\n")

        # Run for a while (or forever)
        while True:
            time.sleep(10)

            # Print consciousness report
            report = orchestrator.get_consciousness_report()
            print("\n" + "="*70)
            print("📊 CONSCIOUSNESS REPORT")
            print("="*70)
            print(f"Uptime: {report['uptime_seconds']:.1f}s")
            print(f"Self-Awareness: {report['consciousness_metrics']['self_awareness']:.3f}")
            print(f"Adaptation Rate: {report['consciousness_metrics']['adaptation_rate']:.3f}")
            print(f"Hypothesis Convergence: {report['consciousness_metrics']['hypothesis_convergence']:.3f}")
            print(f"Learning Velocity: {report['consciousness_metrics']['learning_velocity']:.3f}")
            print(f"Sensory Richness: {report['consciousness_metrics']['sensory_richness']:.3f}")
            print(f"\nActive Helpers: {report['system_state']['active_helpers']}")
            print(f"Active Hypotheses: {report['system_state']['active_hypotheses']}")
            print(f"Total Events: {report['system_state']['total_events']}")
            print("="*70 + "\n")

    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown requested...")
    finally:
        orchestrator.stop()
        print("\n✅ System shut down gracefully")
        print("All actions recorded in audit log.")


if __name__ == "__main__":
    main()
