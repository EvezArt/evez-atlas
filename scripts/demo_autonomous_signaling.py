#!/usr/bin/env python3
"""
Demonstration of Autonomous Entity Signaling System

Shows how entities communicate their status autonomously,
operate without human intervention, and signal when human help is needed.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from skills.entity_lifecycle import EntityLifecycleManager
from skills.jubilee import (
    signal_entities_autonomously,
    get_human_intervention_alerts,
    get_entity_signals
)


def demo_autonomous_signaling():
    """Demonstrate autonomous entity signaling."""

    print("=" * 70)
    print("  AUTONOMOUS ENTITY SIGNALING DEMONSTRATION")
    print("  Communicating Status - Defending Without Human Intervention")
    print("=" * 70)
    print()

    # Step 1: Create entities with different health states
    print("Step 1: Creating Test Entities")
    print("-" * 70)

    manager = EntityLifecycleManager()

    # Healthy entity
    e1 = manager.create_entity('autonomous_worker_1', 'worker', 'default')
    manager.awaken_entity('autonomous_worker_1')
    print("  ✓ Created healthy autonomous worker")

    # Recovering entity (error correction mode)
    e2 = manager.create_entity('autonomous_worker_2', 'defender', 'security')
    manager.awaken_entity('autonomous_worker_2')
    manager.error_correction_mode('autonomous_worker_2')
    print("  ✓ Created recovering defender (defending without human)")

    # Degraded entity
    e3 = manager.create_entity('autonomous_worker_3', 'monitor', 'default')
    manager.awaken_entity('autonomous_worker_3')
    e3_entity = manager.entities['autonomous_worker_3']
    e3_entity.error_count = 7
    manager._save_entity(e3_entity)
    print("  ✓ Created degraded monitor (needs updates)")

    # Critical entity (needs human)
    e4 = manager.create_entity('autonomous_worker_4', 'critical_task', 'security')
    manager.awaken_entity('autonomous_worker_4')
    e4_entity = manager.entities['autonomous_worker_4']
    e4_entity.error_count = 15
    manager._save_entity(e4_entity)
    print("  ✓ Created critical entity (requires human intervention)")

    print()

    # Step 2: Signal all entities autonomously
    print("Step 2: Autonomous Signaling - Communicating Without Human")
    print("-" * 70)

    result = signal_entities_autonomously()

    print(f"  Total entities signaled: {result['total_entities_signaled']}")
    print(f"  Signals sent: {result['signals_sent']}")
    print(f"  Autonomous operations: {result['autonomous_operations']}")
    print(f"  Human intervention required: {result['human_intervention_required']}")

    if result['human_intervention_required'] > 0:
        print("\n  Entities requiring human intervention:")
        for detail in result['intervention_details']:
            print(f"    ⚠️  {detail['entity_id']}: {detail['message']}")

    print()

    # Step 3: Show defending without human
    print("Step 3: Entities Defending Without Human Intervention")
    print("-" * 70)

    defending_signals = get_entity_signals('autonomous_worker_2', limit=5)
    if defending_signals['signal_count'] > 0:
        signal = defending_signals['signals'][0]
        print(f"  Entity: autonomous_worker_2 (defender)")
        print(f"  Status: {signal['message']}")
        print(f"  Type: {signal['type']}")
        print(f"  Requires human: {signal['requires_human']}")
        print("  ✓ Defending autonomously without human intervention")

    print()

    # Step 4: Show update needed signals
    print("Step 4: Entities Communicating Update Needs")
    print("-" * 70)

    update_signals = get_entity_signals('autonomous_worker_3', limit=5)
    if update_signals['signal_count'] > 0:
        signal = update_signals['signals'][0]
        print(f"  Entity: autonomous_worker_3 (monitor)")
        print(f"  Status: {signal['message']}")
        print(f"  Priority: {signal['priority']}")
        print(f"  ✓ Signaling update needs autonomously")

    print()

    # Step 5: Show human intervention alerts
    print("Step 5: Alerting Human When Intervention is Needed")
    print("-" * 70)

    alerts = get_human_intervention_alerts()

    if alerts['alert_count'] > 0:
        print(f"  ⚠️  {alerts['alert_count']} entity(ies) need human intervention:")
        for alert in alerts['alerts']:
            print(f"\n  Entity: {alert['entity_id']}")
            print(f"  Priority: {alert['priority']}")
            print(f"  Message: {alert['message']}")
            print(f"  Action: {alert['data'].get('action_required', 'Review needed')}")
            print("  📧 Human will be notified when sent/available")
    else:
        print("  ✓ All entities operating autonomously")

    print()
    print("=" * 70)
    print("  DEMONSTRATION COMPLETE")
    print("  ✓ Entities signal their status autonomously")
    print("  ✓ Entities defend without human intervention")
    print("  ✓ System alerts when human help is needed")
    print("=" * 70)


if __name__ == '__main__':
    demo_autonomous_signaling()
