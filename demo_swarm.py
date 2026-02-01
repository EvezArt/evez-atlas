#!/usr/bin/env python3
"""
Swarm Demo - Demonstrates autonomous agent capabilities

This script shows how to:
1. Register agents in the swarm
2. Log events to sacred memory
3. Broadcast events to all agents
4. Check quantum backend status
5. Monitor swarm health
"""

import json
import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent))

from skills import (
    log_agent_event,
    register_swarm_agent,
    get_orchestrator,
    get_quantum_integration
)


def main():
    print("🐝 Evez666 Swarm Demo")
    print("=" * 50)
    print()
    
    # 1. Check quantum backend
    print("1. Quantum Backend Status")
    print("-" * 50)
    quantum = get_quantum_integration()
    backend_info = quantum.get_backend_info()
    print(f"   Mode: {backend_info['mode']}")
    print(f"   Backend: {backend_info['backend']}")
    print(f"   Max Qubits: {backend_info['max_qubits']}")
    print(f"   Ready: {backend_info['ready']}")
    print()
    
    # 2. Register agents
    print("2. Registering Agents")
    print("-" * 50)
    
    orchestrator = get_orchestrator()
    
    agent1 = register_swarm_agent(
        "security-scanner",
        skills=["event_logger", "quantum_integration"]
    )
    print(f"   ✓ Registered: {agent1.agent_id}")
    
    agent2 = register_swarm_agent(
        "threat-analyzer",
        skills=["event_logger", "swarm"]
    )
    print(f"   ✓ Registered: {agent2.agent_id}")
    
    agent3 = register_swarm_agent(
        "quantum-detector",
        skills=["event_logger", "quantum_integration"]
    )
    print(f"   ✓ Registered: {agent3.agent_id}")
    print()
    
    # 3. Log some events
    print("3. Logging Events to Sacred Memory")
    print("-" * 50)
    
    event1 = agent1.log_event("security_scan", {
        "target": "network-segment-alpha",
        "threats": 0,
        "duration_ms": 1250
    })
    print(f"   ✓ {agent1.agent_id}: security_scan")
    
    event2 = agent2.log_event("threat_analysis", {
        "source": "security-scanner",
        "risk_level": "low",
        "recommendations": []
    })
    print(f"   ✓ {agent2.agent_id}: threat_analysis")
    
    if quantum.is_quantum_ready():
        event3 = quantum.log_quantum_operation(
            "anomaly_detection",
            qubits=8,
            result={"anomaly_score": 0.15, "confidence": 0.92},
            agent_id=agent3.agent_id
        )
        print(f"   ✓ {agent3.agent_id}: quantum_operation")
    print()
    
    # 4. Broadcast to swarm
    print("4. Broadcasting to Swarm")
    print("-" * 50)
    
    responses = orchestrator.broadcast_event("system_status", {
        "status": "operational",
        "uptime_hours": 24,
        "alerts": []
    })
    print(f"   ✓ Broadcast sent to {len(responses)} agents")
    print()
    
    # 5. Get swarm status
    print("5. Swarm Status")
    print("-" * 50)
    
    status = orchestrator.get_swarm_status()
    print(f"   Swarm ID: {status['swarm_id']}")
    print(f"   Mode: {status['mode']}")
    print(f"   Agent Count: {status['agent_count']}")
    print(f"   Quantum Mode: {status['quantum_mode']}")
    print()
    print("   Agents:")
    for agent_id, agent_status in status['agents'].items():
        print(f"     - {agent_id}")
        print(f"       Skills: {', '.join(agent_status['skills'])}")
        print(f"       Quantum Ready: {agent_status['quantum_ready']}")
    print()
    
    # 6. Summary
    print("6. Summary")
    print("-" * 50)
    print(f"   ✓ {status['agent_count']} agents registered")
    print(f"   ✓ Events logged to data/events.jsonl")
    print(f"   ✓ Quantum backend: {backend_info['backend']}")
    print(f"   ✓ Sacred memory: Persistent")
    print()
    print("Monitor events:")
    print("   tail -f data/events.jsonl")
    print()
    print("Check API status:")
    print("   curl -H 'X-API-Key: tier3_director' http://localhost:8000/swarm-status")
    print()
    print("🎉 Demo complete! Swarm is operational.")


if __name__ == "__main__":
    main()
