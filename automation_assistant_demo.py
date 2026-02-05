"""
Automation Assistant Demo

Demonstrates the usage of the device automation assistant helper system.
Shows how to spawn helpers for different backends and process tasks.
"""

import sys
import time
from automation_assistant import (
    AutomationAssistantManager,
    BackendType,
    HelperConfig,
    create_chatgpt_helper,
    create_comet_helper,
    create_local_helper,
)


def demo_basic_usage():
    """Demonstrate basic usage of the automation assistant."""
    print("=" * 70)
    print("Device Automation Assistant Demo - Basic Usage")
    print("=" * 70)
    
    # Create manager
    manager = AutomationAssistantManager(max_helpers=5)
    
    # Spawn different types of helpers
    print("\n[1] Spawning helpers for different backends...")
    
    chatgpt_id = create_chatgpt_helper(
        manager, 
        name="ChatGPT-Assistant",
        model="gpt-3.5-turbo"
    )
    print(f"    ✓ Spawned ChatGPT helper: {chatgpt_id}")
    
    comet_id = create_comet_helper(
        manager,
        name="Comet-Assistant",
        model="comet-v1"
    )
    print(f"    ✓ Spawned Comet helper: {comet_id}")
    
    local_id = create_local_helper(
        manager,
        name="Local-Assistant"
    )
    print(f"    ✓ Spawned Local helper: {local_id}")
    
    # Display helper statuses
    print("\n[2] Helper status overview:")
    for status in manager.get_all_helpers_status():
        print(f"    - {status['name']}: {status['status']} "
              f"(backend: {status['backend']})")
    
    # Submit tasks to different helpers
    print("\n[3] Submitting tasks to helpers...")
    
    task1_id = manager.submit_task(
        chatgpt_id,
        "Analyze network security patterns",
        context={"source": "firewall_logs", "priority": "high"}
    )
    print(f"    ✓ Submitted task to ChatGPT: {task1_id[:8]}")
    
    task2_id = manager.submit_task(
        comet_id,
        "Generate threat intelligence report",
        context={"timeframe": "24h", "severity": "critical"}
    )
    print(f"    ✓ Submitted task to Comet: {task2_id[:8]}")
    
    task3_id = manager.submit_task(
        local_id,
        "Validate system configuration"
    )
    print(f"    ✓ Submitted task to Local: {task3_id[:8]}")
    
    # Wait for tasks to complete
    print("\n[4] Waiting for task completion...")
    time.sleep(3)
    
    # Retrieve and display results
    print("\n[5] Task results:")
    
    result1 = manager.get_task_result(chatgpt_id, task1_id)
    if result1:
        print(f"\n    ChatGPT Task ({task1_id[:8]}):")
        print(f"    Status: {'Completed' if result1.result else 'Failed'}")
        if result1.result:
            print(f"    Result: {result1.result[:100]}...")
        if result1.error:
            print(f"    Error: {result1.error}")
    
    result2 = manager.get_task_result(comet_id, task2_id)
    if result2:
        print(f"\n    Comet Task ({task2_id[:8]}):")
        print(f"    Status: {'Completed' if result2.result else 'Failed'}")
        if result2.result:
            print(f"    Result: {result2.result[:100]}...")
        if result2.error:
            print(f"    Error: {result2.error}")
    
    result3 = manager.get_task_result(local_id, task3_id)
    if result3:
        print(f"\n    Local Task ({task3_id[:8]}):")
        print(f"    Status: {'Completed' if result3.result else 'Failed'}")
        if result3.result:
            print(f"    Result: {result3.result[:100]}...")
        if result3.error:
            print(f"    Error: {result3.error}")
    
    # Final status
    print("\n[6] Final helper status:")
    for status in manager.get_all_helpers_status():
        print(f"    - {status['name']}: {status['status']} | "
              f"Completed: {status['completed_tasks']}")
    
    # Cleanup
    print("\n[7] Terminating all helpers...")
    manager.terminate_all()
    print("    ✓ All helpers terminated")
    
    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)


def demo_multiple_instances():
    """Demonstrate spawning multiple instances of the same backend."""
    print("\n\n" + "=" * 70)
    print("Device Automation Assistant Demo - Multiple Instances")
    print("=" * 70)
    
    manager = AutomationAssistantManager(max_helpers=10)
    
    print("\n[1] Spawning multiple ChatGPT instances...")
    
    # Spawn multiple ChatGPT helpers with different models
    helpers = []
    for i, model in enumerate(["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]):
        config = HelperConfig(
            backend_type=BackendType.CHATGPT,
            name=f"ChatGPT-{i+1}",
            model=model
        )
        helper_id = manager.spawn_helper(config)
        helpers.append(helper_id)
        print(f"    ✓ Spawned {config.name} with model {model}")
    
    print("\n[2] Submitting parallel tasks...")
    
    tasks = []
    for i, helper_id in enumerate(helpers):
        task_id = manager.submit_task(
            helper_id,
            f"Process request #{i+1}",
            context={"batch": "parallel_demo"}
        )
        tasks.append((helper_id, task_id))
        print(f"    ✓ Task {i+1} submitted to helper {helper_id[:8]}")
    
    print("\n[3] Processing tasks in parallel...")
    time.sleep(2)
    
    print("\n[4] Results:")
    for i, (helper_id, task_id) in enumerate(tasks):
        result = manager.get_task_result(helper_id, task_id)
        if result and result.result:
            print(f"    Task {i+1}: {result.result[:80]}...")
    
    print("\n[5] Cleanup...")
    manager.terminate_all()
    print("    ✓ All helpers terminated")
    
    print("\n" + "=" * 70)


def demo_device_optimized():
    """Demonstrate device-optimized usage with resource constraints."""
    print("\n\n" + "=" * 70)
    print("Device Automation Assistant Demo - Device Optimized")
    print("=" * 70)
    print("(Optimized for Samsung Galaxy A16 and similar devices)")
    
    # Create manager with limited helpers for device constraints
    manager = AutomationAssistantManager(max_helpers=3)
    
    print("\n[1] Creating device-optimized helper pool...")
    
    # Use local backend for offline capability
    local_id = create_local_helper(manager, name="Offline-Helper")
    print(f"    ✓ Local helper (offline capable): {local_id[:8]}")
    
    # One ChatGPT instance for cloud processing
    chatgpt_id = create_chatgpt_helper(
        manager,
        name="Cloud-Helper",
        model="gpt-3.5-turbo"  # More efficient model
    )
    print(f"    ✓ ChatGPT helper (cloud): {chatgpt_id[:8]}")
    
    print("\n[2] Simulating on-device automation tasks...")
    
    # Task 1: Quick local processing
    task1 = manager.submit_task(
        local_id,
        "Check device battery level and optimize settings"
    )
    
    # Task 2: Cloud-based analysis
    task2 = manager.submit_task(
        chatgpt_id,
        "Analyze app usage patterns and suggest optimizations",
        context={"device_model": "Samsung Galaxy A16"}
    )
    
    print("    ✓ Submitted device automation tasks")
    
    print("\n[3] Processing...")
    time.sleep(2)
    
    print("\n[4] Device optimization results:")
    
    result1 = manager.get_task_result(local_id, task1)
    if result1 and result1.result:
        print(f"    Local: {result1.result}")
    
    result2 = manager.get_task_result(chatgpt_id, task2)
    if result2 and result2.result:
        print(f"    Cloud: {result2.result}")
    
    print("\n[5] Resource usage summary:")
    for status in manager.get_all_helpers_status():
        print(f"    - {status['name']}: {status['completed_tasks']} tasks completed")
    
    print("\n[6] Cleanup...")
    manager.terminate_all()
    
    print("\n" + "=" * 70)
    print("Device-optimized demo completed!")
    print("=" * 70)


def main():
    """Run all demo scenarios."""
    try:
        # Run demos
        demo_basic_usage()
        demo_multiple_instances()
        demo_device_optimized()
        
        print("\n\n" + "=" * 70)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nKey Features Demonstrated:")
        print("  ✓ Multi-backend support (ChatGPT, Comet, Local)")
        print("  ✓ Dynamic helper spawning")
        print("  ✓ Parallel task processing")
        print("  ✓ Device-optimized operation")
        print("  ✓ Resource management")
        print("\nThe system is ready for deployment on Samsung Galaxy A16!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check for --debrief flag
    if "--debrief" in sys.argv:
        print("\n" + "=" * 70)
        print("Running debrief after demo completion...")
        print("=" * 70 + "\n")
        main()
        
        # Run debrief script
        import subprocess
        subprocess.run([sys.executable, "scripts/debrief.py"])
    else:
        main()
