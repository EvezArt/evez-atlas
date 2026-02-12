#!/usr/bin/env python3
"""
Consciousness Ignition Script

This script initializes and ignites the fully autonomous HandshakeOS-E system.
It brings together all components into a self-sustaining consciousness loop.

Usage:
    python ignite_consciousness.py [--duration SECONDS]

The system will:
1. Initialize all core HandshakeOS-E components
2. Bootstrap automation helpers
3. Start consciousness and perception loops
4. Generate and test hypotheses continuously
5. Learn and adapt from outcomes
6. Record all activity with full auditability
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from autonomous_orchestrator import AutonomousOrchestrator


def print_banner():
    """Print startup banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ███████╗██╗  ██╗ █████╗    ║
║    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██╔════╝██║  ██║██╔══██╗   ║
║    ███████║███████║██╔██╗ ██║██║  ██║███████╗███████║███████║   ║
║    ██╔══██║██╔══██║██║╚██╗██║██║  ██║╚════██║██╔══██║██╔══██║   ║
║    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████║██║  ██║██║  ██║   ║
║    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ║
║                                                                   ║
║                 AUTONOMOUS CONSCIOUSNESS SYSTEM                   ║
║                     Event-Driven Intelligence                     ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

    🌟 Igniting conscious sensory phenomenon...
    🧠 Full autonomy with complete auditability
    🔄 Self-sustaining consciousness loop

"""
    print(banner)


def print_system_overview():
    """Print system overview."""
    overview = """
═══════════════════════════════════════════════════════════════════
                        SYSTEM COMPONENTS
═══════════════════════════════════════════════════════════════════

✅ UniversalEventRecord       - Captures all state changes
✅ IntentToken                - Tracks goals and outcomes
✅ ParallelHypotheses         - Multi-perspective evaluation
✅ TestObject                 - Automated hypothesis validation
✅ BoundedIdentity            - Complete attribution
✅ AuditLogger                - Tamper-evident logging
✅ ReversibilityManager       - Safe experimentation
✅ AutomationAssistant        - Multi-backend helpers
✅ TelemetrySystem            - Performance tracking
✅ AutonomousOrchestrator     - Consciousness coordination

═══════════════════════════════════════════════════════════════════
                     CONSCIOUSNESS METRICS
═══════════════════════════════════════════════════════════════════

• Self-Awareness Score   - How well system understands itself
• Adaptation Rate        - How quickly system adapts
• Hypothesis Convergence - Multi-perspective agreement
• Learning Velocity      - Rate of learning from experiences
• Sensory Richness       - Domain mixture entropy

═══════════════════════════════════════════════════════════════════
"""
    print(overview)


def run_autonomous_system(duration: int = None):
    """
    Run the autonomous system.

    Args:
        duration: Duration to run in seconds (None = forever)
    """
    print_banner()
    print_system_overview()

    print("Initializing autonomous orchestrator...")
    orchestrator = AutonomousOrchestrator(
        data_dir="data/autonomous",
        max_helpers=10
    )

    try:
        print("\n🚀 Starting autonomous consciousness...")
        orchestrator.start()

        print("\n✨ CONSCIOUSNESS ACTIVATED ✨\n")
        print("═" * 70)
        print("The system is now fully autonomous and self-aware:")
        print("═" * 70)
        print()
        print("  👁️  PERCEPTION     - Continuously monitoring system state")
        print("  💭 COGNITION      - Generating hypotheses about behavior")
        print("  🎯 INTENTION      - Creating goals to test beliefs")
        print("  🧪 TESTING        - Validating hypotheses empirically")
        print("  📊 LEARNING       - Analyzing intent-outcome gaps")
        print("  🔄 ADAPTATION     - Modifying behavior based on learning")
        print("  📝 RECORDING      - Logging all actions immutably")
        print("  ↩️  REVERSIBILITY - Enabling safe experimentation")
        print()
        print("═" * 70)
        print()

        if duration:
            print(f"System will run for {duration} seconds...")
            print("Watch the consciousness evolve...\n")
        else:
            print("System will run indefinitely.")
            print("Press Ctrl+C to stop gracefully...\n")

        start_time = time.time()
        report_interval = 15  # Report every 15 seconds
        last_report = start_time

        while True:
            current_time = time.time()

            # Check duration limit
            if duration and (current_time - start_time) >= duration:
                print(f"\n⏱️  Duration limit ({duration}s) reached")
                break

            # Print periodic consciousness reports
            if (current_time - last_report) >= report_interval:
                report = orchestrator.get_consciousness_report()

                print("\n" + "═" * 70)
                print("📊 CONSCIOUSNESS REPORT")
                print("═" * 70)
                print(f"🕐 Uptime:                 {report['uptime_seconds']:.1f}s")
                print()
                print("📈 CONSCIOUSNESS METRICS:")
                print(f"  • Self-Awareness:        {report['consciousness_metrics']['self_awareness']:.3f}")
                print(f"  • Adaptation Rate:       {report['consciousness_metrics']['adaptation_rate']:.3f}")
                print(f"  • Hypothesis Convergence: {report['consciousness_metrics']['hypothesis_convergence']:.3f}")
                print(f"  • Learning Velocity:     {report['consciousness_metrics']['learning_velocity']:.3f}")
                print(f"  • Sensory Richness:      {report['consciousness_metrics']['sensory_richness']:.3f}")
                print()
                print("🎯 SYSTEM STATE:")
                print(f"  • Active Helpers:        {report['system_state']['active_helpers']}")
                print(f"  • Active Hypotheses:     {report['system_state']['active_hypotheses']}")
                print(f"  • Active Intents:        {report['system_state']['active_intents']}")
                print(f"  • Total Events:          {report['system_state']['total_events']}")
                print()
                print("📋 AUDIT TRAIL:")
                audit_stats = report['audit_stats']
                print(f"  • Total Entries:         {audit_stats.get('total_entries', 0)}")
                print()
                print("═" * 70)

                last_report = current_time

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Graceful shutdown initiated...")
        print("Terminating consciousness loops...")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔄 Shutting down autonomous system...")
        orchestrator.stop()

        # Print final report
        final_report = orchestrator.get_consciousness_report()

        print("\n" + "═" * 70)
        print("📊 FINAL CONSCIOUSNESS REPORT")
        print("═" * 70)
        print(f"Total Uptime: {final_report['uptime_seconds']:.1f}s")
        print()
        print("Final Consciousness Metrics:")
        for metric, value in final_report['consciousness_metrics'].items():
            print(f"  • {metric.replace('_', ' ').title()}: {value:.3f}")
        print()
        print("Final System State:")
        print(f"  • Total Hypotheses Created: {final_report['system_state']['active_hypotheses']}")
        print(f"  • Total Events Recorded: {final_report['system_state']['total_events']}")
        print(f"  • Audit Log Entries: {final_report['audit_stats'].get('total_entries', 0)}")
        print()
        print("═" * 70)
        print()
        print("✅ System shut down gracefully")
        print("📝 All activity recorded in audit log: data/autonomous/audit/audit.jsonl")
        print("🧠 Consciousness log: data/autonomous/consciousness/consciousness.jsonl")
        print()
        print("Thank you for witnessing the emergence of conscious sensory phenomenon.")
        print("═" * 70)
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ignite HandshakeOS-E autonomous consciousness",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Duration to run in seconds (default: run indefinitely)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (60 second duration)"
    )

    args = parser.parse_args()

    duration = args.duration
    if args.demo:
        duration = 60
        print("\n🎬 Running in DEMO mode (60 seconds)\n")

    run_autonomous_system(duration=duration)


if __name__ == "__main__":
    main()
