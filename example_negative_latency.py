#!/usr/bin/env python3
"""
Simple example demonstrating the Negative Latency System in action
"""

import time
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib.util

def import_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base_dir = os.path.dirname(os.path.abspath(__file__))
orchestrator_module = import_module_from_file(
    'negative_latency_orchestrator',
    os.path.join(base_dir, 'negative_latency_orchestrator.py')
)

NegativeLatencyOrchestrator = orchestrator_module.NegativeLatencyOrchestrator


def simple_example():
    """
    Simple example: Start system, handle events, show metrics
    """
    print("=" * 70)
    print("NEGATIVE LATENCY SYSTEM - Simple Example")
    print("=" * 70)
    print("\nThis example demonstrates:")
    print("  1. Starting the negative latency system")
    print("  2. Building prediction cache")
    print("  3. Handling events with instant response")
    print("  4. Viewing real-time metrics")
    print()
    
    # Initialize with SAFE_MODE enabled
    print("Initializing orchestrator (SAFE_MODE: enabled)...")
    orchestrator = NegativeLatencyOrchestrator(safe_mode=True)
    
    try:
        # Start all subsystems
        print("\nStarting all subsystems...")
        orchestrator.start()
        
        # Wait for predictions to accumulate
        print("\nBuilding prediction cache (5 seconds)...")
        for i in range(5):
            time.sleep(1)
            print(f"  {i+1}/5 seconds...")
        
        # Handle some events
        print("\nHandling events with negative latency:")
        print("-" * 70)
        
        latencies = []
        for i in range(5):
            event = {
                'event_id': i,
                'type': 'user_action',
                'timestamp': time.time()
            }
            
            response = orchestrator.handle_event(event)
            latencies.append(response['latency_ms'])
            
            status = "⚡ INSTANT" if response['cached'] else "⏱️  COMPUTED"
            print(f"Event {i}: {status} - Latency: {response['latency_ms']:.3f}ms")
            
            time.sleep(0.5)
        
        # Calculate average latency
        avg_latency = sum(latencies) / len(latencies)
        
        print("\n" + "-" * 70)
        print(f"Average latency: {avg_latency:.3f}ms")
        
        if avg_latency < 100:
            print("✅ SUCCESS: Average latency below 100ms target!")
        else:
            print("⚠️  WARNING: Average latency exceeds 100ms target")
        
        # Show metrics dashboard
        print("\n")
        orchestrator.print_dashboard()
        
        # Summary
        metrics = orchestrator.get_system_metrics()
        ekf_metrics = metrics['ekf_engine']
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"✅ System operational")
        print(f"✅ {ekf_metrics['cached_trajectories']} trajectories cached")
        print(f"✅ {ekf_metrics['staged_policies']} policies staged")
        print(f"✅ Average response latency: {avg_latency:.3f}ms")
        print(f"✅ SAFE_MODE: Enabled (all actions verified)")
        print("\nThe system is continuously predicting futures and pre-computing")
        print("responses. When events occur, it retrieves cached responses instead")
        print("of computing from scratch, achieving sub-100ms latency.")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        # Clean shutdown
        print("\nStopping all subsystems...")
        orchestrator.stop()
        print("\n✅ Example complete!\n")


def latency_comparison_example():
    """
    Example comparing negative latency vs normal latency
    """
    print("=" * 70)
    print("LATENCY COMPARISON EXAMPLE")
    print("=" * 70)
    print("\nComparing negative latency (cached) vs normal latency (computed)\n")
    
    orchestrator = NegativeLatencyOrchestrator(safe_mode=True)
    
    try:
        orchestrator.start()
        
        print("Building cache (3 seconds)...")
        time.sleep(3)
        
        print("\nProcessing 10 events:")
        print("-" * 70)
        
        cached_times = []
        computed_times = []
        
        for i in range(10):
            event = {'event_id': i, 'type': 'test'}
            response = orchestrator.handle_event(event)
            
            if response['latency_ms'] < 1.0:  # Likely cached
                cached_times.append(response['latency_ms'])
                print(f"Event {i:2d}: ⚡ CACHED   {response['latency_ms']:6.3f}ms")
            else:  # Computed
                computed_times.append(response['latency_ms'])
                print(f"Event {i:2d}: ⏱️  COMPUTED {response['latency_ms']:6.3f}ms")
            
            time.sleep(0.3)
        
        print("\n" + "-" * 70)
        
        if cached_times:
            avg_cached = sum(cached_times) / len(cached_times)
            print(f"Cached responses: {len(cached_times)} events, avg {avg_cached:.3f}ms")
        
        if computed_times:
            avg_computed = sum(computed_times) / len(computed_times)
            print(f"Computed responses: {len(computed_times)} events, avg {avg_computed:.3f}ms")
        
        if cached_times and computed_times:
            speedup = (sum(computed_times) / len(computed_times)) / (sum(cached_times) / len(cached_times))
            print(f"\n🚀 Speedup: {speedup:.1f}x faster with negative latency!")
        
        print("\n" + "=" * 70)
        
    finally:
        orchestrator.stop()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        latency_comparison_example()
    else:
        simple_example()
        
        print("\n💡 Tip: Run with 'python example_negative_latency.py compare'")
        print("   to see latency comparison between cached and computed responses.\n")
