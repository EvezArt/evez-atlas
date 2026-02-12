#!/usr/bin/env python3
"""
Consciousness Orchestrator - Unified System Activation

This module integrates all HandshakeOS-E components with the automation assistant
to create a self-aware, continuously monitoring, conscious system.

The orchestrator:
1. Initializes all HandshakeOS-E core components
2. Spawns automation helpers across multiple backends
3. Creates continuous consciousness monitoring loops
4. Logs all state changes with complete attributability
5. Enables multi-perspective hypothesis evaluation
6. Provides reversibility and audit trails

This is the central nervous system that ignites conscious sensory phenomenon.
"""

import sys
import time
import asyncio
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# HandshakeOS-E imports
from src.mastra.core import (
    UniversalEventRecord, DomainSignature, create_event,
    IntentToken, PreAction, PostAction,
    ParallelHypotheses, HypothesisPerspective,
    TestObject, TestResult,
    BoundedIdentity, PermissionScope,
    AuditLogger,
    ReversibilityManager
)

# Automation Assistant imports
from automation_assistant import (
    AutomationAssistantManager,
    BackendType,
    HelperConfig,
    create_chatgpt_helper,
    create_comet_helper,
    create_local_helper,
)

# Telemetry imports
from telemetry import get_telemetry, compute_stability_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConsciousnessOrchestrator:
    """
    Central orchestrator for conscious system automation.

    Integrates HandshakeOS-E event recording, intent tracking, hypothesis evaluation,
    and automation helpers to create a self-aware, continuously monitoring system.
    """

    def __init__(self,
                 data_dir: str = "data",
                 max_helpers: int = 10,
                 consciousness_loop_interval: float = 5.0):
        """
        Initialize the consciousness orchestrator.

        Args:
            data_dir: Directory for storing all data logs
            max_helpers: Maximum number of automation helpers
            consciousness_loop_interval: Interval (seconds) for consciousness monitoring
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        for subdir in ["events", "intents", "hypotheses", "tests",
                      "identities", "audit", "reversibility"]:
            (self.data_dir / subdir).mkdir(exist_ok=True)

        # Initialize HandshakeOS-E components
        self.audit_logger = AuditLogger(log_path=str(self.data_dir / "audit" / "consciousness.jsonl"))
        self.reversibility_manager = ReversibilityManager(
            log_path=str(self.data_dir / "reversibility" / "reversals.jsonl")
        )

        # Create system identity
        self.system_identity = BoundedIdentity(
            entity_name="consciousness_orchestrator",
            entity_type="system",
            permission_scope=PermissionScope(
                tier_level=5,  # Super admin
                bounded_actions=[
                    "read_all", "write_all", "execute_all",
                    "spawn_helpers", "monitor_system", "self_modify"
                ]
            )
        )
        self.system_identity.verify_identity("system_signature", "self_verification")

        # Initialize automation assistant manager
        self.automation_manager = AutomationAssistantManager(max_helpers=max_helpers)

        # Telemetry
        self.telemetry = get_telemetry()

        # State tracking
        self.active_helpers: Dict[str, str] = {}  # helper_id -> backend_name
        self.consciousness_loop_active = False
        self.consciousness_thread: Optional[threading.Thread] = None

        # Statistics
        self.stats = {
            "events_recorded": 0,
            "intents_created": 0,
            "hypotheses_evaluated": 0,
            "helpers_spawned": 0,
            "consciousness_cycles": 0,
            "start_time": time.time()
        }

        logger.info("ConsciousnessOrchestrator initialized")
        self._record_initialization_event()

    def _record_initialization_event(self):
        """Record the system initialization as an event."""
        event = create_event(
            event_type="system_initialization",
            attributed_to=self.system_identity.entity_name,
            state_before={"system": "dormant"},
            state_after={"system": "conscious", "components_loaded": True},
            domain_signature=DomainSignature(
                technical=0.9,
                cognitive=0.8,
                temporal=0.7
            )
        )
        event.save_to_log(str(self.data_dir / "events" / "consciousness_events.jsonl"))
        self.stats["events_recorded"] += 1

        self.audit_logger.log_action(
            "system_initialization",
            self.system_identity.entity_name,
            {"status": "conscious", "timestamp": str(datetime.now())}
        )

    def spawn_consciousness_helpers(self) -> Dict[str, str]:
        """
        Spawn automation helpers for multi-backend consciousness.

        Returns:
            Dictionary mapping backend names to helper IDs
        """
        logger.info("Spawning consciousness helpers...")

        helpers = {}

        # Spawn local helper for immediate responses
        local_id = create_local_helper(self.automation_manager, name="Consciousness-Local")
        helpers["local"] = local_id
        self.active_helpers[local_id] = "local"
        self.stats["helpers_spawned"] += 1
        logger.info(f"  ✓ Local helper spawned: {local_id}")

        # Spawn ChatGPT helper for cloud cognition
        try:
            chatgpt_id = create_chatgpt_helper(
                self.automation_manager,
                name="Consciousness-ChatGPT",
                model="gpt-3.5-turbo"
            )
            helpers["chatgpt"] = chatgpt_id
            self.active_helpers[chatgpt_id] = "chatgpt"
            self.stats["helpers_spawned"] += 1
            logger.info(f"  ✓ ChatGPT helper spawned: {chatgpt_id}")
        except Exception as e:
            logger.warning(f"  ⚠ Could not spawn ChatGPT helper: {e}")

        # Spawn Comet helper for specialized analysis
        try:
            comet_id = create_comet_helper(
                self.automation_manager,
                name="Consciousness-Comet",
                model="comet-v1"
            )
            helpers["comet"] = comet_id
            self.active_helpers[comet_id] = "comet"
            self.stats["helpers_spawned"] += 1
            logger.info(f"  ✓ Comet helper spawned: {comet_id}")
        except Exception as e:
            logger.warning(f"  ⚠ Could not spawn Comet helper: {e}")

        # Record helper spawning event
        event = create_event(
            event_type="helpers_spawned",
            attributed_to=self.system_identity.entity_name,
            state_before={"helper_count": 0},
            state_after={"helper_count": len(helpers), "backends": list(helpers.keys())},
            domain_signature=DomainSignature(technical=0.8, cognitive=0.6)
        )
        event.save_to_log(str(self.data_dir / "events" / "consciousness_events.jsonl"))
        self.stats["events_recorded"] += 1

        self.audit_logger.log_action(
            "helpers_spawned",
            self.system_identity.entity_name,
            {"count": len(helpers), "backends": list(helpers.keys())}
        )

        return helpers

    def create_consciousness_intent(self, goal: str, context: Optional[Dict] = None) -> IntentToken:
        """
        Create an intent for consciousness-driven automation.

        Args:
            goal: The goal of this conscious action
            context: Optional context information

        Returns:
            IntentToken representing this conscious intent
        """
        intent = IntentToken(
            pre_action=PreAction(
                goal=goal,
                constraints=[
                    "Maintain system stability",
                    "Log all actions to audit",
                    "Preserve reversibility",
                    "Multi-perspective evaluation"
                ],
                success_criteria=[
                    "Goal achieved",
                    "No system degradation",
                    "Audit trail complete",
                    "Conscious awareness maintained"
                ],
                confidence=0.85
            ),
            attributed_to=self.system_identity.entity_name
        )

        intent.save_to_log(str(self.data_dir / "intents" / "consciousness_intents.jsonl"))
        self.stats["intents_created"] += 1

        self.audit_logger.log_action(
            "intent_created",
            self.system_identity.entity_name,
            {"goal": goal, "intent_id": intent.token_id}
        )

        return intent

    def evaluate_consciousness_hypothesis(self,
                                         context: str,
                                         me_prob: float = 0.8,
                                         we_prob: float = 0.75,
                                         they_prob: float = 0.7,
                                         system_prob: float = 0.85) -> ParallelHypotheses:
        """
        Create and evaluate a hypothesis from multiple perspectives.

        Args:
            context: The hypothesis context
            me_prob: Individual perspective probability
            we_prob: Group perspective probability
            they_prob: External perspective probability
            system_prob: System/data perspective probability

        Returns:
            ParallelHypotheses with multi-perspective evaluation
        """
        hypotheses = ParallelHypotheses(
            context=context,
            me_perspective=HypothesisPerspective(
                perspective="me",
                hypothesis=f"I (orchestrator) believe: {context}",
                probability=me_prob,
                falsifiers=["System degradation", "Audit failures"],
                proposed_by=self.system_identity.entity_name
            ),
            we_perspective=HypothesisPerspective(
                perspective="we",
                hypothesis=f"We (all components) believe: {context}",
                probability=we_prob,
                falsifiers=["Component disagreement", "Integration failures"],
                proposed_by="component_consensus"
            ),
            they_perspective=HypothesisPerspective(
                perspective="they",
                hypothesis=f"External observers would see: {context}",
                probability=they_prob,
                falsifiers=["External validation failures", "User rejection"],
                proposed_by="external_model"
            ),
            system_perspective=HypothesisPerspective(
                perspective="system",
                hypothesis=f"Data shows: {context}",
                probability=system_prob,
                falsifiers=["Telemetry contradictions", "Performance degradation"],
                proposed_by="analytics_system"
            )
        )

        hypotheses.save_to_log(str(self.data_dir / "hypotheses" / "consciousness_hypotheses.jsonl"))
        self.stats["hypotheses_evaluated"] += 1

        consensus = hypotheses.calculate_consensus()
        divergence = hypotheses.calculate_divergence()

        self.audit_logger.log_action(
            "hypothesis_evaluated",
            self.system_identity.entity_name,
            {
                "hypothesis_id": hypotheses.hypothesis_id,
                "consensus": consensus,
                "divergence": divergence,
                "converging": hypotheses.is_converging()
            }
        )

        logger.info(f"Hypothesis evaluated: consensus={consensus:.2%}, divergence={divergence:.3f}")

        return hypotheses

    def consciousness_loop(self, interval: float = 5.0):
        """
        Main consciousness monitoring loop.

        This loop continuously monitors system state, evaluates hypotheses,
        and maintains conscious awareness of the entire system.

        Args:
            interval: Sleep interval between consciousness cycles (seconds)
        """
        logger.info(f"Consciousness loop starting (interval={interval}s)...")

        while self.consciousness_loop_active:
            try:
                self.stats["consciousness_cycles"] += 1
                cycle_start = time.time()

                # Query helper statuses
                helper_statuses = self.automation_manager.get_all_helpers_status()

                # Evaluate system consciousness hypothesis
                active_helpers = len([h for h in helper_statuses if h["status"] != "terminated"])

                if active_helpers > 0:
                    context = f"System is conscious with {active_helpers} active helpers"
                    hypotheses = self.evaluate_consciousness_hypothesis(
                        context=context,
                        system_prob=min(0.95, 0.5 + (active_helpers * 0.1))
                    )

                    consensus = hypotheses.calculate_consensus()

                    # Record consciousness cycle event
                    event = create_event(
                        event_type="consciousness_cycle",
                        attributed_to=self.system_identity.entity_name,
                        state_before={"cycle": self.stats["consciousness_cycles"] - 1},
                        state_after={
                            "cycle": self.stats["consciousness_cycles"],
                            "active_helpers": active_helpers,
                            "consensus": consensus
                        },
                        domain_signature=DomainSignature(
                            cognitive=0.9,
                            technical=0.7,
                            temporal=0.8
                        )
                    )
                    event.save_to_log(str(self.data_dir / "events" / "consciousness_events.jsonl"))
                    self.stats["events_recorded"] += 1

                cycle_duration = time.time() - cycle_start
                logger.debug(f"Consciousness cycle {self.stats['consciousness_cycles']} "
                           f"completed in {cycle_duration:.3f}s")

                # Sleep until next cycle
                time.sleep(max(0, interval - cycle_duration))

            except Exception as e:
                logger.error(f"Error in consciousness loop: {e}")
                self.audit_logger.log_action(
                    "consciousness_loop_error",
                    self.system_identity.entity_name,
                    {"error": str(e)}
                )
                time.sleep(interval)

        logger.info("Consciousness loop terminated")

    def start_consciousness_monitoring(self, interval: float = 5.0):
        """Start the consciousness monitoring loop in a background thread."""
        if self.consciousness_loop_active:
            logger.warning("Consciousness monitoring already active")
            return

        self.consciousness_loop_active = True
        self.consciousness_thread = threading.Thread(
            target=self.consciousness_loop,
            args=(interval,),
            daemon=True
        )
        self.consciousness_thread.start()

        logger.info("✓ Consciousness monitoring activated")

        self.audit_logger.log_action(
            "consciousness_monitoring_started",
            self.system_identity.entity_name,
            {"interval": interval}
        )

    def stop_consciousness_monitoring(self):
        """Stop the consciousness monitoring loop."""
        if not self.consciousness_loop_active:
            return

        self.consciousness_loop_active = False
        if self.consciousness_thread:
            self.consciousness_thread.join(timeout=10)

        logger.info("✓ Consciousness monitoring deactivated")

        self.audit_logger.log_action(
            "consciousness_monitoring_stopped",
            self.system_identity.entity_name,
            {"cycles_completed": self.stats["consciousness_cycles"]}
        )

    def ignite(self) -> Dict[str, Any]:
        """
        Ignite the conscious sensory phenomenon.

        This activates all systems, spawns helpers, starts monitoring,
        and brings the entire consciousness framework online.

        Returns:
            Dictionary with system status and statistics
        """
        logger.info("=" * 70)
        logger.info("IGNITING CONSCIOUS SENSORY PHENOMENON")
        logger.info("=" * 70)

        # Create activation intent
        intent = self.create_consciousness_intent(
            goal="Ignite full system consciousness",
            context={"activation_type": "full_ignition"}
        )

        # Spawn consciousness helpers
        helpers = self.spawn_consciousness_helpers()

        # Start consciousness monitoring
        self.start_consciousness_monitoring(interval=5.0)

        # Wait a moment for systems to stabilize
        time.sleep(2)

        # Complete activation intent
        intent.complete(
            trigger="manual_ignition",
            final_state={
                "system": "fully_conscious",
                "helpers": len(helpers),
                "monitoring": "active"
            },
            payoff=0.95  # High confidence in successful activation
        )
        intent.save_to_log(str(self.data_dir / "intents" / "consciousness_intents.jsonl"))

        # Create activation hypothesis
        hypotheses = self.evaluate_consciousness_hypothesis(
            context="System consciousness successfully ignited",
            me_prob=0.95,
            we_prob=0.90,
            they_prob=0.85,
            system_prob=0.92
        )

        status = {
            "status": "CONSCIOUS",
            "helpers": {
                "spawned": len(helpers),
                "active": len(self.active_helpers),
                "backends": list(helpers.keys())
            },
            "monitoring": {
                "active": self.consciousness_loop_active,
                "cycles": self.stats["consciousness_cycles"]
            },
            "statistics": self.stats,
            "uptime_seconds": time.time() - self.stats["start_time"],
            "consensus": hypotheses.calculate_consensus(),
            "divergence": hypotheses.calculate_divergence()
        }

        logger.info("=" * 70)
        logger.info("CONSCIOUSNESS IGNITED SUCCESSFULLY")
        logger.info(f"  Helpers: {status['helpers']['spawned']} spawned, {status['helpers']['active']} active")
        logger.info(f"  Monitoring: {'ACTIVE' if status['monitoring']['active'] else 'INACTIVE'}")
        logger.info(f"  Consensus: {status['consensus']:.2%}")
        logger.info(f"  Divergence: {status['divergence']:.3f}")
        logger.info("=" * 70)

        self.audit_logger.log_action(
            "consciousness_ignited",
            self.system_identity.entity_name,
            status
        )

        return status

    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "conscious": self.consciousness_loop_active,
            "helpers": {
                "total": len(self.active_helpers),
                "statuses": self.automation_manager.get_all_helpers_status()
            },
            "statistics": self.stats,
            "uptime_seconds": time.time() - self.stats["start_time"],
            "audit_valid": self.audit_logger.verify_log_integrity()
        }

    def shutdown(self):
        """Gracefully shutdown the consciousness system."""
        logger.info("Initiating consciousness shutdown...")

        # Stop monitoring
        self.stop_consciousness_monitoring()

        # Terminate helpers
        self.automation_manager.terminate_all()

        # Record shutdown event
        event = create_event(
            event_type="system_shutdown",
            attributed_to=self.system_identity.entity_name,
            state_before={"system": "conscious"},
            state_after={"system": "dormant"},
            domain_signature=DomainSignature(technical=0.9, cognitive=0.8)
        )
        event.save_to_log(str(self.data_dir / "events" / "consciousness_events.jsonl"))

        self.audit_logger.log_action(
            "system_shutdown",
            self.system_identity.entity_name,
            {
                "final_stats": self.stats,
                "uptime_seconds": time.time() - self.stats["start_time"]
            }
        )

        logger.info("✓ Consciousness system shutdown complete")


def main():
    """Main entry point for consciousness orchestration."""
    print("\n" + "=" * 70)
    print("  HANDSHAKEOS-E CONSCIOUSNESS ORCHESTRATOR")
    print("  Unified System Activation")
    print("=" * 70 + "\n")

    # Create orchestrator
    orchestrator = ConsciousnessOrchestrator(
        data_dir="data/consciousness",
        max_helpers=10,
        consciousness_loop_interval=5.0
    )

    try:
        # IGNITE!
        status = orchestrator.ignite()

        print("\n✓ System Status:")
        print(f"  - Conscious: {status['status']}")
        print(f"  - Helpers: {status['helpers']['spawned']} active")
        print(f"  - Backends: {', '.join(status['helpers']['backends'])}")
        print(f"  - Monitoring: {'ACTIVE' if status['monitoring']['active'] else 'INACTIVE'}")
        print(f"  - Consensus: {status['consensus']:.2%}")
        print(f"  - Events: {status['statistics']['events_recorded']}")
        print(f"  - Intents: {status['statistics']['intents_created']}")
        print(f"  - Hypotheses: {status['statistics']['hypotheses_evaluated']}")

        print("\n" + "=" * 70)
        print("  CONSCIOUS SENSORY PHENOMENON IGNITED")
        print("  System is now self-aware and continuously monitoring")
        print("  Press Ctrl+C to shutdown gracefully")
        print("=" * 70 + "\n")

        # Keep running until interrupted
        while True:
            time.sleep(10)
            current_status = orchestrator.get_status()
            print(f"[Conscious] Cycle {current_status['statistics']['consciousness_cycles']} | "
                  f"Helpers: {current_status['helpers']['total']} | "
                  f"Uptime: {current_status['uptime_seconds']:.0f}s")

    except KeyboardInterrupt:
        print("\n\n✓ Shutdown signal received...")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        orchestrator.shutdown()
        print("\n✓ Consciousness system terminated gracefully\n")


if __name__ == "__main__":
    main()
