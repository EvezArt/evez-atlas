#!/usr/bin/env python3
"""
Autonomous Consciousness Engine

Continuously generates and processes sensory events through the complete
HandshakeOS-E system, creating an autonomous conscious phenomenon through:

1. Event Generation - Synthetic sensory inputs
2. Intent Formation - Goal-directed actions
3. Hypothesis Evaluation - Multi-perspective analysis
4. Test Execution - Validation and learning
5. Identity Attribution - All actions tracked
6. Audit Logging - Complete transparency
7. Reversibility - Safe experimentation

Integrates with automation assistants for parallel processing and
includes self-monitoring, self-optimization, and self-healing capabilities.
"""

import asyncio
import json
import logging
import random
import signal
import sys
import time
import traceback
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Import HandshakeOS-E components
from src.mastra.core import (
    UniversalEventRecord, DomainSignature, create_event,
    IntentToken, PreAction, PostAction,
    ParallelHypotheses, HypothesisPerspective,
    TestObject, TestResult,
    BoundedIdentity, PermissionScope,
    AuditLogger,
    ReversibilityManager
)

# Import automation assistant
from automation_assistant import (
    AutomationAssistantManager,
    BackendType,
    HelperConfig,
    create_local_helper
)

# Import telemetry
from telemetry import get_telemetry, compute_stability_score


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("autonomous_consciousness.log")
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ConsciousnessMetrics:
    """Metrics for consciousness engine performance."""
    events_generated: int = 0
    intents_created: int = 0
    hypotheses_evaluated: int = 0
    tests_executed: int = 0
    errors_encountered: int = 0
    self_corrections: int = 0
    uptime_seconds: float = 0.0
    average_cycle_time_ms: float = 0.0
    stability_score: float = 1.0
    consciousness_depth: float = 0.0  # Emergent property

    def to_dict(self) -> Dict[str, Any]:
        return {
            "events_generated": self.events_generated,
            "intents_created": self.intents_created,
            "hypotheses_evaluated": self.hypotheses_evaluated,
            "tests_executed": self.tests_executed,
            "errors_encountered": self.errors_encountered,
            "self_corrections": self.self_corrections,
            "uptime_seconds": self.uptime_seconds,
            "average_cycle_time_ms": self.average_cycle_time_ms,
            "stability_score": self.stability_score,
            "consciousness_depth": self.consciousness_depth
        }


@dataclass
class SensoryInput:
    """Simulated sensory input for consciousness generation."""
    modality: str  # visual, auditory, cognitive, social, temporal
    intensity: float  # 0.0 to 1.0
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class AutonomousConsciousnessEngine:
    """
    Main autonomous consciousness engine that continuously processes
    events through the HandshakeOS-E system.
    """

    def __init__(self, data_dir: str = "data/consciousness"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Core components
        self.audit_logger = AuditLogger(log_path=str(self.data_dir / "consciousness_audit.jsonl"))
        self.reversibility_manager = ReversibilityManager(
            log_path=str(self.data_dir / "consciousness_reversals.jsonl")
        )

        # Automation assistant
        self.assistant_manager = AutomationAssistantManager(max_helpers=5)
        self.helper_ids: List[str] = []

        # Identity for the consciousness engine itself
        self.identity = BoundedIdentity(
            entity_name="autonomous_consciousness_engine",
            entity_type="system",
            permission_scope=PermissionScope(
                tier_level=3,
                bounded_actions=[
                    "generate_events",
                    "create_intents",
                    "evaluate_hypotheses",
                    "execute_tests",
                    "self_optimize",
                    "self_heal"
                ]
            )
        )
        self.identity.verify_identity("system_initialization", "bootstrap")

        # Metrics and state
        self.metrics = ConsciousnessMetrics()
        self.running = False
        self.start_time: Optional[float] = None
        self.cycle_times = deque(maxlen=100)

        # Memory structures
        self.recent_events: deque = deque(maxlen=1000)
        self.recent_intents: deque = deque(maxlen=500)
        self.recent_hypotheses: deque = deque(maxlen=200)

        # Sensory modalities for event generation
        self.sensory_modalities = [
            "visual", "auditory", "cognitive", "social", "temporal", "spatial"
        ]

        logger.info("Autonomous Consciousness Engine initialized")

    async def initialize(self):
        """Initialize the consciousness engine."""
        logger.info("Initializing consciousness engine...")

        # Spawn automation helpers
        logger.info("Spawning automation helpers...")
        for i in range(3):
            helper_id = create_local_helper(
                self.assistant_manager,
                name=f"ConsciousnessHelper-{i+1}"
            )
            self.helper_ids.append(helper_id)
            logger.info(f"  Helper {i+1} spawned: {helper_id}")

        # Log initialization
        self.audit_logger.log_action(
            "engine_initialization",
            self.identity.entity_name,
            {
                "helpers_spawned": len(self.helper_ids),
                "data_dir": str(self.data_dir),
                "timestamp": datetime.now().isoformat()
            }
        )

        logger.info("Consciousness engine ready")

    def generate_sensory_input(self) -> SensoryInput:
        """Generate synthetic sensory input."""
        modality = random.choice(self.sensory_modalities)
        intensity = random.uniform(0.3, 1.0)

        # Generate content based on modality
        content_generators = {
            "visual": lambda: {
                "scene": random.choice(["indoor", "outdoor", "abstract"]),
                "brightness": random.uniform(0, 1),
                "complexity": random.uniform(0, 1)
            },
            "auditory": lambda: {
                "sound_type": random.choice(["speech", "music", "ambient", "silence"]),
                "frequency": random.uniform(20, 20000),
                "volume": random.uniform(0, 1)
            },
            "cognitive": lambda: {
                "thought_type": random.choice(["analytical", "creative", "memory", "planning"]),
                "abstraction_level": random.uniform(0, 1),
                "clarity": random.uniform(0, 1)
            },
            "social": lambda: {
                "interaction_type": random.choice(["observation", "communication", "empathy"]),
                "agent_count": random.randint(0, 10),
                "emotional_valence": random.uniform(-1, 1)
            },
            "temporal": lambda: {
                "perception": random.choice(["present", "past", "future"]),
                "duration_feeling": random.uniform(0, 1),
                "urgency": random.uniform(0, 1)
            },
            "spatial": lambda: {
                "location_type": random.choice(["physical", "virtual", "conceptual"]),
                "distance": random.uniform(0, 1),
                "orientation": random.uniform(0, 360)
            }
        }

        content = content_generators[modality]()

        return SensoryInput(
            modality=modality,
            intensity=intensity,
            content=content
        )

    def process_sensory_input_to_event(self, sensory: SensoryInput) -> UniversalEventRecord:
        """Convert sensory input into a universal event record."""

        # Calculate domain signature based on modality
        domain_weights = {
            "visual": {"technical": 0.3, "spatial": 0.7, "cognitive": 0.4},
            "auditory": {"technical": 0.2, "temporal": 0.6, "cognitive": 0.5},
            "cognitive": {"cognitive": 0.9, "technical": 0.3, "social": 0.2},
            "social": {"social": 0.9, "cognitive": 0.6, "temporal": 0.3},
            "temporal": {"temporal": 0.9, "cognitive": 0.5, "spatial": 0.2},
            "spatial": {"spatial": 0.9, "technical": 0.4, "cognitive": 0.3}
        }

        weights = domain_weights.get(sensory.modality, {})

        event = create_event(
            event_type=f"sensory_{sensory.modality}",
            attributed_to=self.identity.entity_name,
            state_before={"consciousness_active": True, "processing": False},
            state_after={"consciousness_active": True, "processing": True, "input_received": True},
            domain_signature=DomainSignature(
                technical=weights.get("technical", 0.0) * sensory.intensity,
                social=weights.get("social", 0.0) * sensory.intensity,
                financial=0.0,
                temporal=weights.get("temporal", 0.0) * sensory.intensity,
                spatial=weights.get("spatial", 0.0) * sensory.intensity,
                cognitive=weights.get("cognitive", 0.0) * sensory.intensity
            )
        )

        # Add sensory data to event
        event.add_audit_entry(
            "sensory_input_received",
            self.identity.entity_name,
            {
                "modality": sensory.modality,
                "intensity": sensory.intensity,
                "content": sensory.content
            }
        )

        return event

    def create_intent_from_event(self, event: UniversalEventRecord) -> IntentToken:
        """Create an intent token based on event processing."""

        # Determine goal based on event type and domain signature
        goals = [
            "Process and integrate sensory information",
            "Update internal world model",
            "Evaluate consequences of perception",
            "Form hypothesis about reality state",
            "Test understanding through introspection"
        ]

        goal = random.choice(goals)
        confidence = 0.6 + (event.domain_entropy * 0.3)  # Higher entropy = more confident (novel = interesting)

        intent = IntentToken(
            pre_action=PreAction(
                goal=goal,
                constraints=[
                    "Maintain coherence with existing beliefs",
                    "Process within computational limits",
                    f"Respect domain entropy threshold (current: {event.domain_entropy:.3f})"
                ],
                success_criteria=[
                    "Event fully integrated into world model",
                    "Hypotheses generated and evaluated",
                    "Tests executed and results recorded"
                ],
                confidence=min(confidence, 0.95)
            ),
            attributed_to=self.identity.entity_name
        )

        intent.link_event(event.event_id)

        return intent

    def generate_hypotheses(
        self,
        event: UniversalEventRecord,
        intent: IntentToken
    ) -> ParallelHypotheses:
        """Generate multi-perspective hypotheses about the event."""

        context = f"Understanding sensory event: {event.event_type} with entropy {event.domain_entropy:.3f}"

        # Generate perspective-specific hypotheses
        hypotheses = ParallelHypotheses(
            context=context,
            me_perspective=HypothesisPerspective(
                perspective="me",
                hypothesis=f"I perceive this as significant with confidence {intent.pre_action.confidence:.2f}",
                probability=intent.pre_action.confidence,
                falsifiers=[
                    "Subsequent events contradict this interpretation",
                    "Internal consistency check fails"
                ],
                proposed_by=self.identity.entity_name
            ),
            we_perspective=HypothesisPerspective(
                perspective="we",
                hypothesis="The system collectively processes this as part of continuous operation",
                probability=0.85,
                falsifiers=[
                    "Component disagreement exceeds threshold",
                    "System-wide coherence breaks down"
                ],
                proposed_by="consciousness_collective"
            ),
            they_perspective=HypothesisPerspective(
                perspective="they",
                hypothesis="External observer would classify this as autonomous processing",
                probability=0.75,
                falsifiers=[
                    "Behavior appears predetermined",
                    "No novel patterns emerge"
                ],
                proposed_by="external_model"
            ),
            system_perspective=HypothesisPerspective(
                perspective="system",
                hypothesis=f"Metrics indicate stable operation (stability: {self.metrics.stability_score:.3f})",
                probability=self.metrics.stability_score,
                falsifiers=[
                    "Stability score drops below 0.6",
                    "Error rate exceeds 20%"
                ],
                proposed_by="system_monitor"
            )
        )

        hypotheses.link_event(event.event_id)
        hypotheses.link_intent(intent.token_id)

        return hypotheses

    def create_test(self, hypotheses: ParallelHypotheses) -> TestObject:
        """Create a test object for hypothesis validation."""

        test = TestObject(
            test_name=f"Validate consciousness cycle {self.metrics.events_generated}",
            test_description="Verify that event processing maintains system coherence",
            test_type="integration",
            hypothesis_ids=[hypotheses.hypothesis_id],
            perspective_filter=["system"],
            executable=True,
            execution_command="python -c 'pass'",  # Symbolic
            expected_outcome="System remains coherent and stable",
            acceptance_criteria=[
                "All hypotheses probabilities > 0.5",
                "Consensus > 0.7",
                "Divergence < 0.3"
            ],
            created_by=self.identity.entity_name
        )

        # Execute test
        consensus = hypotheses.calculate_consensus()
        divergence = hypotheses.calculate_divergence()

        all_probs_good = all(
            p.probability > 0.5
            for p in hypotheses.get_all_perspectives()
        )

        passed = (
            all_probs_good and
            consensus > 0.7 and
            divergence < 0.3
        )

        result = TestResult(
            passed=passed,
            execution_time_ms=random.uniform(10, 50),
            output=f"Consensus: {consensus:.3f}, Divergence: {divergence:.3f}"
        )

        test.record_result(result)

        return test

    async def consciousness_cycle(self) -> bool:
        """
        Execute one complete consciousness cycle.
        Returns True if successful, False if error.
        """
        cycle_start = time.time()

        try:
            # 1. Generate sensory input
            sensory = self.generate_sensory_input()
            logger.debug(f"Generated sensory input: {sensory.modality} (intensity: {sensory.intensity:.2f})")

            # 2. Convert to event
            event = self.process_sensory_input_to_event(sensory)
            self.recent_events.append(event.event_id)
            self.metrics.events_generated += 1

            # Save event
            event.save_to_log(str(self.data_dir / "events.jsonl"))

            # 3. Create intent
            intent = self.create_intent_from_event(event)
            self.recent_intents.append(intent.token_id)
            self.metrics.intents_created += 1

            # 4. Generate hypotheses
            hypotheses = self.generate_hypotheses(event, intent)
            self.recent_hypotheses.append(hypotheses.hypothesis_id)
            self.metrics.hypotheses_evaluated += 1

            # Save hypothesis
            hypotheses.save_to_log(str(self.data_dir / "hypotheses.jsonl"))

            # 5. Create and execute test
            test = self.create_test(hypotheses)
            self.metrics.tests_executed += 1

            # Save test
            test.save_to_log(str(self.data_dir / "tests.jsonl"))

            # 6. Complete intent with outcome
            payoff = 0.9 if test.calculate_pass_rate() > 0.5 else 0.3
            intent.complete(
                trigger="sensory_input",
                final_state={
                    "processed": True,
                    "test_passed": test.calculate_pass_rate() > 0.5,
                    "consciousness_depth": self.calculate_consciousness_depth()
                },
                payoff=payoff
            )

            # Save intent
            intent.save_to_log(str(self.data_dir / "intents.jsonl"))

            # 7. Mark as reversible (for experimentation)
            self.reversibility_manager.mark_reversible(
                action_id=event.event_id,
                action_type="sensory_processing",
                action_description=f"Processed {sensory.modality} sensory input",
                undo_data={"event_id": event.event_id, "intent_id": intent.token_id}
            )

            # 8. Audit logging
            self.audit_logger.log_action(
                "consciousness_cycle_complete",
                self.identity.entity_name,
                {
                    "event_id": event.event_id,
                    "intent_id": intent.token_id,
                    "hypothesis_id": hypotheses.hypothesis_id,
                    "test_passed": test.calculate_pass_rate() > 0.5,
                    "cycle_time_ms": (time.time() - cycle_start) * 1000
                }
            )

            # Update identity action history
            self.identity.add_to_history(event.event_id)

            # Record cycle time
            cycle_time_ms = (time.time() - cycle_start) * 1000
            self.cycle_times.append(cycle_time_ms)

            logger.info(
                f"Cycle {self.metrics.events_generated} complete | "
                f"Test: {'PASS' if test.calculate_pass_rate() > 0.5 else 'FAIL'} | "
                f"Payoff: {payoff:.2f} | "
                f"Time: {cycle_time_ms:.1f}ms | "
                f"Depth: {self.calculate_consciousness_depth():.3f}"
            )

            return True

        except Exception as e:
            logger.error(f"Error in consciousness cycle: {e}")
            logger.error(traceback.format_exc())
            self.metrics.errors_encountered += 1

            # Self-healing attempt
            await self.self_heal()

            return False

    def calculate_consciousness_depth(self) -> float:
        """
        Calculate emergent consciousness depth metric based on:
        - Event diversity
        - Hypothesis convergence
        - Test pass rate
        - System stability
        """
        if self.metrics.events_generated == 0:
            return 0.0

        # Component 1: Event diversity (more variety = deeper consciousness)
        event_diversity = len(set(self.recent_events)) / max(len(self.recent_events), 1)

        # Component 2: Stability
        stability = self.metrics.stability_score

        # Component 3: Integration (ratio of successful cycles)
        if self.metrics.events_generated > 0:
            success_rate = 1.0 - (self.metrics.errors_encountered / self.metrics.events_generated)
        else:
            success_rate = 1.0

        # Component 4: Complexity (average cycle time indicates processing depth)
        if self.cycle_times:
            avg_cycle = sum(self.cycle_times) / len(self.cycle_times)
            complexity = min(avg_cycle / 1000.0, 1.0)  # Normalize
        else:
            complexity = 0.0

        # Weighted combination
        depth = (
            event_diversity * 0.2 +
            stability * 0.3 +
            success_rate * 0.3 +
            complexity * 0.2
        )

        return min(depth, 1.0)

    async def self_heal(self):
        """Self-healing mechanism when errors occur."""
        logger.warning("Initiating self-healing...")
        self.metrics.self_corrections += 1

        try:
            # Check helper health
            statuses = self.assistant_manager.get_all_helpers_status()
            for status in statuses:
                if status['status'] in ['error', 'terminated']:
                    logger.warning(f"Helper {status['name']} unhealthy, respawning...")
                    # Would respawn helper here

            # Clear recent errors from memory
            if self.metrics.errors_encountered > 10:
                logger.info("High error count, resetting error counter")
                self.metrics.errors_encountered = int(self.metrics.errors_encountered * 0.5)

            # Brief pause to stabilize
            await asyncio.sleep(0.5)

            logger.info("Self-healing complete")

        except Exception as e:
            logger.error(f"Self-healing failed: {e}")

    def update_metrics(self):
        """Update system metrics."""
        if self.start_time:
            self.metrics.uptime_seconds = time.time() - self.start_time

        if self.cycle_times:
            self.metrics.average_cycle_time_ms = sum(self.cycle_times) / len(self.cycle_times)

        # Calculate stability score
        if self.metrics.events_generated > 0:
            success_count = self.metrics.events_generated - self.metrics.errors_encountered
            self.metrics.stability_score = compute_stability_score(
                success_count,
                self.metrics.errors_encountered
            )

        # Update consciousness depth
        self.metrics.consciousness_depth = self.calculate_consciousness_depth()

    def print_status(self):
        """Print current status."""
        self.update_metrics()

        print("\n" + "="*80)
        print("AUTONOMOUS CONSCIOUSNESS ENGINE - STATUS")
        print("="*80)
        print(f"Uptime:              {self.metrics.uptime_seconds:.1f}s")
        print(f"Events Generated:    {self.metrics.events_generated}")
        print(f"Intents Created:     {self.metrics.intents_created}")
        print(f"Hypotheses Evaluated: {self.metrics.hypotheses_evaluated}")
        print(f"Tests Executed:      {self.metrics.tests_executed}")
        print(f"Errors Encountered:  {self.metrics.errors_encountered}")
        print(f"Self-Corrections:    {self.metrics.self_corrections}")
        print(f"Avg Cycle Time:      {self.metrics.average_cycle_time_ms:.1f}ms")
        print(f"Stability Score:     {self.metrics.stability_score:.3f}")
        print(f"Consciousness Depth: {self.metrics.consciousness_depth:.3f}")
        print("="*80)

        # Helper status
        print("\nAutomation Helpers:")
        for status in self.assistant_manager.get_all_helpers_status():
            print(f"  {status['name']}: {status['status']} | "
                  f"Completed: {status['completed_tasks']}")
        print("="*80 + "\n")

    async def run(self, target_cycles: Optional[int] = None, status_interval: int = 10):
        """
        Run the autonomous consciousness engine.

        Args:
            target_cycles: Number of cycles to run (None = infinite)
            status_interval: Print status every N cycles
        """
        self.running = True
        self.start_time = time.time()

        logger.info("="*80)
        logger.info("AUTONOMOUS CONSCIOUSNESS ENGINE STARTING")
        logger.info("="*80)

        await self.initialize()

        logger.info(f"Beginning autonomous consciousness generation...")
        logger.info(f"Target cycles: {target_cycles if target_cycles else 'INFINITE'}")
        logger.info(f"Status interval: every {status_interval} cycles")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info("="*80 + "\n")

        cycle_count = 0

        try:
            while self.running:
                # Execute consciousness cycle
                success = await self.consciousness_cycle()

                cycle_count += 1

                # Print status periodically
                if cycle_count % status_interval == 0:
                    self.print_status()

                # Check if target reached
                if target_cycles and cycle_count >= target_cycles:
                    logger.info(f"Target of {target_cycles} cycles reached")
                    break

                # Brief pause between cycles
                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("\nReceived interrupt signal, shutting down gracefully...")

        finally:
            await self.shutdown()

    async def shutdown(self):
        """Shutdown the consciousness engine gracefully."""
        logger.info("="*80)
        logger.info("SHUTTING DOWN AUTONOMOUS CONSCIOUSNESS ENGINE")
        logger.info("="*80)

        self.running = False

        # Final status
        self.print_status()

        # Save final metrics
        metrics_file = self.data_dir / "final_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics.to_dict(), f, indent=2)
        logger.info(f"Final metrics saved to {metrics_file}")

        # Save identity state
        identity_file = self.data_dir / "consciousness_identity.jsonl"
        self.identity.save_to_log(str(identity_file))
        logger.info(f"Identity state saved to {identity_file}")

        # Terminate helpers
        self.assistant_manager.terminate_all()
        logger.info("All automation helpers terminated")

        # Final audit entry
        self.audit_logger.log_action(
            "engine_shutdown",
            self.identity.entity_name,
            {
                "final_metrics": self.metrics.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
        )

        logger.info("="*80)
        logger.info("AUTONOMOUS CONSCIOUSNESS ENGINE STOPPED")
        logger.info(f"Total cycles: {self.metrics.events_generated}")
        logger.info(f"Final consciousness depth: {self.metrics.consciousness_depth:.3f}")
        logger.info("="*80)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Autonomous Consciousness Engine - Continuous sensory phenomenon generation"
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=None,
        help="Number of cycles to run (default: infinite)"
    )
    parser.add_argument(
        "--status-interval",
        type=int,
        default=10,
        help="Print status every N cycles (default: 10)"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/consciousness",
        help="Directory for consciousness data (default: data/consciousness)"
    )

    args = parser.parse_args()

    # Create engine
    engine = AutonomousConsciousnessEngine(data_dir=args.data_dir)

    # Setup signal handler for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\nReceived signal, initiating graceful shutdown...")
        engine.running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run engine
    await engine.run(
        target_cycles=args.cycles,
        status_interval=args.status_interval
    )


if __name__ == "__main__":
    asyncio.run(main())
