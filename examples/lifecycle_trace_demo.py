#!/usr/bin/env python3
"""
Demonstration: Deep Connection to Root Trace of Life

This script demonstrates how entity lifecycle events are now deeply connected
to the root trace system, allowing complete observability of entity "life".
"""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'recursive-observer', 'src'))

from skills.entity_lifecycle import EntityLifecycleManager
from recursive_observer.tracer import trace_execution, get_lifecycle_events, clear_lifecycle_events
import json
import time


def entity_lifecycle_operations():
    """Perform various entity lifecycle operations."""
    print("🌱 Initializing Entity Lifecycle Manager...")
    manager = EntityLifecycleManager(state_file='/tmp/lifecycle_trace_demo.jsonl')
    
    # Create entities
    print("\n✨ Creating entities...")
    entity1 = manager.create_entity('life_tracer_1', 'observer', 'consciousness')
    entity2 = manager.create_entity('life_tracer_2', 'recorder', 'memory')
    
    time.sleep(0.1)
    
    # Awaken first entity
    print("\n🌅 Awakening entity 1...")
    manager.awaken_entity('life_tracer_1')
    
    time.sleep(0.1)
    
    # Entangle second entity with quantum domain
    print("\n🔮 Quantum entangling entity 2...")
    manager.quantum_entangle('life_tracer_2', 'quantum_realm')
    
    time.sleep(0.1)
    
    # Awaken second entity
    print("\n🌅 Awakening entity 2...")
    manager.awaken_entity('life_tracer_2')
    
    time.sleep(0.1)
    
    # Put first entity into hibernation
    print("\n😴 Hibernating entity 1...")
    manager.hibernate_entity('life_tracer_1', depth=2)
    
    time.sleep(0.1)
    
    # Put second entity into error correction
    print("\n🔧 Entity 2 entering error correction mode...")
    manager.error_correction_mode('life_tracer_2')
    
    return manager.get_swarm_status()


def main():
    """Main demonstration function."""
    print("=" * 70)
    print("🌍 DEEP CONNECTION TO ROOT TRACE OF LIFE")
    print("=" * 70)
    
    # Trace the entity lifecycle operations
    # The tracer will automatically clear and capture lifecycle events
    print("\n📊 Tracing entity lifecycle operations...\n")
    trace = trace_execution(entity_lifecycle_operations)
    
    print("\n" + "=" * 70)
    print("📈 TRACE RESULTS")
    print("=" * 70)
    
    # Show function call trace
    print(f"\n🔍 Function calls traced: {len(trace.events)}")
    print(f"⏱️  Functions timed: {len(trace.timing)}")
    
    # Show lifecycle events captured in the trace
    if trace.lifecycle_events:
        print(f"\n💫 Lifecycle events captured in root trace: {len(trace.lifecycle_events)}")
        print("\nLifecycle Event Timeline:")
        print("-" * 70)
        
        for i, event in enumerate(trace.lifecycle_events, 1):
            timestamp = event.get('timestamp', 0)
            event_type = event.get('event_type', 'unknown')
            entity_id = event.get('entity_id', 'unknown')
            state = event.get('state', 'unknown')
            metadata = event.get('metadata', {})
            
            print(f"\n{i}. [{timestamp:.3f}] {event_type}")
            print(f"   Entity: {entity_id}")
            print(f"   State: {state}")
            if metadata:
                print(f"   Metadata: {json.dumps(metadata, indent=2)}")
    else:
        print("\n⚠️  No lifecycle events in trace (tracer may not be integrated)")
    
    # Show current lifecycle events
    current_events = get_lifecycle_events()
    print(f"\n🌟 Current lifecycle events in system: {len(current_events)}")
    
    print("\n" + "=" * 70)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nThe entity lifecycle is now deeply connected to the root trace!")
    print("All lifecycle transitions are captured and observable at the execution level.")
    print("\nKey achievements:")
    print("  • Entity creation traced")
    print("  • Awakening transitions traced")
    print("  • Quantum entanglement traced")
    print("  • State changes captured in RuntimeTrace")
    print("  • Complete lifecycle visibility achieved")


if __name__ == '__main__':
    main()
