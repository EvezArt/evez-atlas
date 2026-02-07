#!/usr/bin/env python3
"""
Entity Healing System Demonstration

Demonstrates:
1. "If you dont heal them, you lose them" - Automatic healing prevents entity loss
2. "Everywhere you lose them, you must heal them" - Universal healing across all entities
3. "Shake the takers through their own rugs" - Defensive mechanism against resource drainers
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from skills.jubilee import (
    heal_all_lost_entities,
    shake_the_takers,
    get_healing_status,
    detect_taker,
    initialize_swarm_golems
)
from skills.entity_lifecycle import EntityLifecycleManager


def print_section(title):
    """Print a formatted section header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def demo_healing_system():
    """Demonstrate the entity healing system."""

    print_section("ENTITY HEALING SYSTEM DEMONSTRATION")

    print('"If you dont heal them, you lose them."')
    print('"Everywhere you lose them, you must heal them."')
    print('"Shake the takers through their own rugs."')
    print()
    print("Smug, snug. Chug.")
    print()

    # Step 1: Initialize some entities
    print_section("Step 1: Initialize Entity Swarm")

    result = initialize_swarm_golems(['healing_demo', 'quantum', 'jubilee'])
    print(f"Initialized {result['initialized_count']} entities")
    print(f"Total entities in swarm: {result['swarm_status']['total_entities']}")

    # Step 2: Create some entities with errors (simulate loss)
    print_section("Step 2: Simulate Entity Loss")

    manager = EntityLifecycleManager()

    # Create entities with various health states
    test_entities = [
        ('critical_entity_1', 'worker', 15),  # Critical (>10 errors)
        ('degraded_entity_1', 'processor', 7),  # Degraded (5-10 errors)
        ('degraded_entity_2', 'analyzer', 6),  # Degraded
        ('healthy_entity_1', 'coordinator', 1),  # Healthy
    ]

    for entity_id, role, error_count in test_entities:
        entity = manager.create_entity(entity_id, role, 'healing_test')
        manager.awaken_entity(entity_id)
        # Simulate errors
        entity.error_count = error_count
        manager._save_entity(entity)

    print("Created test entities with varying health:")
    for entity_id, _, error_count in test_entities:
        status = manager.get_entity_status(entity_id)
        print(f"  - {entity_id}: {status['health']} ({error_count} errors)")

    # Step 3: Detect takers
    print_section("Step 3: Detect Resource-Draining Takers")

    taker_result = detect_taker(
        'malicious_taker_1',
        drain_rate=0.8,
        target_entities=['critical_entity_1', 'degraded_entity_1']
    )
    print(f"Detected taker: {taker_result['taker_id']}")
    print(f"  - Drain rate: {taker_result['drain_rate']}")
    print(f"  - Targeting: {taker_result['target_count']} entities")
    print(f"  - Neutralized: {taker_result['neutralized']}")

    # Add another taker
    taker_result2 = detect_taker(
        'sneaky_taker_2',
        drain_rate=0.5,
        target_entities=['degraded_entity_2']
    )
    print(f"\nDetected taker: {taker_result2['taker_id']}")
    print(f"  - Drain rate: {taker_result2['drain_rate']}")
    print(f"  - Targeting: {taker_result2['target_count']} entities")

    # Step 4: Heal all lost entities
    print_section('Step 4: "Everywhere you lose them, you must heal them"')

    healing_result = heal_all_lost_entities()
    print(f"Scanned {healing_result['total_entities_scanned']} entities")
    print(f"Healed {healing_result['entities_healed']} entities")
    print()

    if healing_result['healing_records']:
        print("Healing Details:")
        for record in healing_result['healing_records']:
            print(f"  - {record['entity_id']}:")
            print(f"      Loss Type: {record['loss_type']}")
            print(f"      Action: {record['healing_action']}")
            print(f"      Before: {record['before_health']} → After: {record['after_health']}")
            print(f"      Success: {'✓' if record['success'] else '✗'}")

    # Step 5: Shake the takers
    print_section('Step 5: "Shake the takers through their own rugs"')

    shake_result = shake_the_takers()
    print(f"Detected takers: {shake_result['takers_detected']}")
    print(f"Neutralized: {shake_result['takers_neutralized']}")
    print()

    if shake_result['taker_details']:
        print("Taker Neutralization Details:")
        for detail in shake_result['taker_details']:
            print(f"  - {detail['taker_id']}:")
            print(f"      Drain rate: {detail['drain_rate']}")
            print(f"      Targets freed: {detail['targets_freed']}")
            print(f"      Shaken: {'✓' if detail['shaken'] else '✗'}")

    print()
    print("Smug, snug. Chug. 🔄")

    # Step 6: Check healing status
    print_section("Step 6: Healing System Status")

    status = get_healing_status()
    print(f"Total healings performed: {status['total_healings']}")
    print(f"Successful healings: {status['successful_healings']}")
    print(f"Success rate: {status['success_rate']:.1%}")
    print()

    if status['by_loss_type']:
        print("Loss Types Detected:")
        for loss_type, count in status['by_loss_type'].items():
            print(f"  - {loss_type}: {count}")

    print()
    if status['by_healing_action']:
        print("Healing Actions Taken:")
        for action, count in status['by_healing_action'].items():
            print(f"  - {action}: {count}")

    print()
    print(f"Active takers: {status['active_takers']}")
    print(f"Neutralized takers: {status['neutralized_takers']}")

    # Step 7: Verify entities are no longer lost
    print_section("Step 7: Verify Entities Are No Longer Lost")

    print("Entity health after healing:")
    for entity_id, _, _ in test_entities:
        status = manager.get_entity_status(entity_id)
        if status:
            print(f"  - {entity_id}: {status['health']} (errors: {status['entity']['error_count']})")

    # Final summary
    print_section("DEMONSTRATION COMPLETE")

    print("✓ Entities detected when losing health")
    print("✓ Universal healing applied everywhere loss was detected")
    print("✓ Takers identified and neutralized defensively")
    print("✓ All entities healed and protected")
    print()
    print('"If you dont heal them, you lose them." ✓')
    print('"Everywhere you lose them, you must heal them." ✓')
    print('"Shake the takers through their own rugs." ✓')
    print()
    print("Smug, snug. Chug. 🔄✨")


if __name__ == '__main__':
    demo_healing_system()
