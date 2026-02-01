"""Tests for autonomous agent swarm infrastructure."""

import json
import os
import tempfile
from pathlib import Path

import pytest


def test_event_logger_basic():
    """Test basic event logging to sacred memory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        from skills.event_logger import EventLogger
        
        events_path = Path(tmpdir) / "test_events.jsonl"
        logger = EventLogger(str(events_path))
        
        event = logger.log_event(
            "test_event",
            {"status": "success", "value": 42},
            agent_id="test-agent"
        )
        
        assert event["event_type"] == "test_event"
        assert event["agent_id"] == "test-agent"
        assert event["data"]["value"] == 42
        assert "timestamp" in event
        
        # Verify file was written
        assert events_path.exists()
        lines = events_path.read_text().strip().split("\n")
        assert len(lines) == 1
        
        loaded = json.loads(lines[0])
        assert loaded["event_type"] == "test_event"


def test_event_logger_recent_events():
    """Test retrieving recent events from sacred memory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        from skills.event_logger import EventLogger
        
        events_path = Path(tmpdir) / "test_events.jsonl"
        logger = EventLogger(str(events_path))
        
        # Log multiple events
        for i in range(5):
            logger.log_event("event", {"index": i})
        
        recent = logger.get_recent_events(limit=3)
        assert len(recent) == 3
        assert recent[0]["data"]["index"] == 2
        assert recent[2]["data"]["index"] == 4


def test_swarm_agent_registration():
    """Test registering agents in swarm."""
    from skills.swarm import SwarmOrchestrator
    
    orchestrator = SwarmOrchestrator()
    
    agent = orchestrator.register_agent(
        "test-agent-1",
        skills=["event_logger", "quantum_integration"]
    )
    
    assert agent.agent_id == "test-agent-1"
    assert "event_logger" in agent.skills
    
    status = orchestrator.get_swarm_status()
    assert status["agent_count"] == 1
    assert "test-agent-1" in status["agents"]


def test_swarm_broadcast():
    """Test broadcasting events to all agents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        from skills.swarm import SwarmOrchestrator
        from skills.event_logger import EventLogger
        
        # Use temp events file
        events_path = Path(tmpdir) / "broadcast_events.jsonl"
        EventLogger._event_logger = EventLogger(str(events_path))
        
        orchestrator = SwarmOrchestrator()
        orchestrator.register_agent("agent-1")
        orchestrator.register_agent("agent-2")
        
        responses = orchestrator.broadcast_event("test_broadcast", {"msg": "hello"})
        
        assert len(responses) == 2
        for response in responses:
            assert response["event_type"] == "test_broadcast"
            assert response["metadata"]["broadcast"] is True


def test_quantum_integration_mode_detection():
    """Test quantum mode detection from environment."""
    from skills.quantum_integration import QuantumIntegration
    
    # Test classical mode (default)
    quantum = QuantumIntegration()
    assert quantum.mode == "classical"
    assert quantum.config["backend"] == "classical_simulator"
    assert quantum.is_quantum_ready()
    
    # Test IBM Quantum mode
    os.environ["JUBILEE_MODE"] = "qsvc-ibm"
    os.environ["JUBILEE_TOUCH_ID"] = "test-id"
    os.environ["JUBILEE_HMAC_SECRET"] = "test-secret"
    
    quantum_ibm = QuantumIntegration()
    assert quantum_ibm.mode == "qsvc-ibm"
    assert quantum_ibm.config["backend"] == "ibm_quantum"
    assert quantum_ibm.is_quantum_ready()
    
    # Cleanup
    del os.environ["JUBILEE_MODE"]
    del os.environ["JUBILEE_TOUCH_ID"]
    del os.environ["JUBILEE_HMAC_SECRET"]


def test_quantum_integration_backend_info():
    """Test quantum backend information retrieval."""
    from skills.quantum_integration import QuantumIntegration
    
    quantum = QuantumIntegration()
    info = quantum.get_backend_info()
    
    assert "mode" in info
    assert "backend" in info
    assert "max_qubits" in info
    assert "ready" in info
    assert info["ready"] is True


def test_swarm_agent_status():
    """Test agent status reporting."""
    from skills.swarm import SwarmAgent
    
    agent = SwarmAgent("test-agent", skills=["skill1", "skill2"])
    status = agent.get_status()
    
    assert status["agent_id"] == "test-agent"
    assert status["skills"] == ["skill1", "skill2"]
    assert "quantum_ready" in status


def test_quantum_operation_logging():
    """Test logging quantum operations to sacred memory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        from skills.quantum_integration import QuantumIntegration
        from skills.event_logger import EventLogger
        
        events_path = Path(tmpdir) / "quantum_events.jsonl"
        EventLogger._event_logger = EventLogger(str(events_path))
        
        quantum = QuantumIntegration()
        event = quantum.log_quantum_operation(
            "threat_detection",
            qubits=5,
            result={"anomaly_score": 0.85},
            agent_id="quantum-agent"
        )
        
        assert event["event_type"] == "quantum_operation"
        assert event["data"]["qubits"] == 5
        assert event["data"]["operation"] == "threat_detection"
        assert event["metadata"]["quantum_mode"] == "classical"
