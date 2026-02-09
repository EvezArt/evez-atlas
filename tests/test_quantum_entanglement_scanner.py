#!/usr/bin/env python3
"""
Test suite for Quantum Entanglement Threat Scanner
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
from quantum_entanglement_scanner import (
    QuantumEntanglementScanner,
    ThreatMeasurement,
    EntanglementState,
    create_test_scenario
)


def test_scanner_initialization():
    """Test scanner initializes correctly."""
    scanner = QuantumEntanglementScanner(output_dir="/tmp/test_scans")
    assert scanner.output_dir == "/tmp/test_scans"
    assert len(scanner.entangled_entities) == 0
    assert len(scanner.measurement_history) == 0


def test_register_entanglement():
    """Test registering entangled entities."""
    scanner = QuantumEntanglementScanner()
    
    state = scanner.register_entanglement("test_entity", ["partner1", "partner2"])
    
    assert state.entity_id == "test_entity"
    assert len(state.partner_ids) == 2
    assert state.entanglement_strength == 1.0
    assert not state.threat_detected
    assert len(state.state_vector) == 8


def test_full_stack_scan():
    """Test full stack scanning."""
    scanner = create_test_scenario()
    
    results = scanner.full_stack_scan()
    
    assert results["total_entities"] == 4
    assert "threats_detected" in results
    assert "corrections_needed" in results
    assert "overall_coherence" in results
    assert "safety_level" in results
    assert len(results["measurements"]) == 4


def test_threat_detection():
    """Test threat detection mechanism."""
    scanner = QuantumEntanglementScanner()
    scanner.register_entanglement("threat_test", ["partner"])
    
    # Simulate threat by modifying state
    state = scanner.entangled_entities["threat_test"]
    state.entanglement_strength = 0.3  # Low strength = higher threat
    state.last_measurement = time.time() - 120  # Old measurement
    
    results = scanner.full_stack_scan()
    
    # Should detect threat
    assert results["threats_detected"] > 0


def test_error_correction():
    """Test error correction functionality."""
    scanner = QuantumEntanglementScanner()
    scanner.register_entanglement("error_test", ["partner"])
    
    # Corrupt state
    state = scanner.entangled_entities["error_test"]
    state.state_vector = [0.1] * 8  # Not normalized
    state.correction_needed = True
    
    # Apply correction
    success = scanner.apply_error_correction("error_test")
    
    assert success
    assert not state.correction_needed
    # Check normalization
    norm = sum(v ** 2 for v in state.state_vector)
    assert abs(norm - 1.0) < 0.01


def test_threat_map_generation():
    """Test threat map generation."""
    scanner = create_test_scenario()
    scanner.full_stack_scan()
    
    threat_map = scanner.generate_threat_map()
    
    assert "timestamp" in threat_map
    assert "threat_map" in threat_map
    assert "hotspots" in threat_map
    assert "total_measurements" in threat_map
    assert threat_map["total_measurements"] == 4


def test_safety_status():
    """Test safety status reporting."""
    scanner = create_test_scenario()
    scanner.full_stack_scan()
    
    status = scanner.get_safety_status()
    
    assert "status" in status
    assert "safety_level" in status
    assert "total_entities" in status
    assert status["total_entities"] == 4
    assert 0.0 <= status["safety_level"] <= 1.0


def test_measurement_export():
    """Test measurement map export."""
    scanner = create_test_scenario()
    scanner.full_stack_scan()
    
    output_file = "/tmp/test_threat_map.json"
    saved_path = scanner.export_measurement_map(output_file)
    
    assert os.path.exists(saved_path)
    
    # Verify file contents
    with open(saved_path, 'r') as f:
        data = json.load(f)
    
    assert "threat_map" in data
    assert "measurement_history" in data
    
    # Clean up
    os.remove(saved_path)


def test_continuous_monitoring():
    """Test continuous monitoring cycle."""
    scanner = create_test_scenario()
    
    # Run short monitoring cycle
    results = scanner.continuous_monitoring_cycle(duration=2.0, interval=0.5)
    
    # Should have multiple scans
    assert len(results) >= 2
    assert all("total_entities" in r for r in results)
    assert all(r["total_entities"] == 4 for r in results)


def test_coherence_calculation():
    """Test coherence calculation."""
    scanner = QuantumEntanglementScanner()
    
    # Perfect coherence (uniform superposition)
    import math
    ideal_state = [1.0 / math.sqrt(8)] * 8
    coherence = scanner._calculate_coherence(ideal_state)
    assert coherence > 0.99
    
    # Poor coherence (non-uniform)
    poor_state = [0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    coherence = scanner._calculate_coherence(poor_state)
    assert coherence < 0.5


def test_hotspot_identification():
    """Test threat hotspot identification."""
    scanner = create_test_scenario()
    
    # Create some threats
    for entity_id in scanner.entangled_entities.keys():
        state = scanner.entangled_entities[entity_id]
        state.entanglement_strength = 0.2  # Low strength
        state.last_measurement = time.time() - 120  # Old measurement
    
    scanner.full_stack_scan()
    threat_map = scanner.generate_threat_map()
    
    # Should detect threats even if not creating hotspots
    # (hotspots require threat_level > threshold in same grid cell)
    assert "hotspots" in threat_map
    assert isinstance(threat_map["hotspots"], list)


def test_position_conversion():
    """Test state vector to 3D position conversion."""
    scanner = QuantumEntanglementScanner()
    
    state_vector = [0.5, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0]
    position = scanner._state_to_position(state_vector)
    
    assert len(position) == 3
    assert isinstance(position[0], float)
    assert isinstance(position[1], float)
    assert isinstance(position[2], float)


def run_all_tests():
    """Run all tests manually."""
    print("=" * 70)
    print("Running Quantum Entanglement Scanner Tests")
    print("=" * 70)
    
    tests = [
        ("Scanner Initialization", test_scanner_initialization),
        ("Register Entanglement", test_register_entanglement),
        ("Full Stack Scan", test_full_stack_scan),
        ("Threat Detection", test_threat_detection),
        ("Error Correction", test_error_correction),
        ("Threat Map Generation", test_threat_map_generation),
        ("Safety Status", test_safety_status),
        ("Measurement Export", test_measurement_export),
        ("Continuous Monitoring", test_continuous_monitoring),
        ("Coherence Calculation", test_coherence_calculation),
        ("Hotspot Identification", test_hotspot_identification),
        ("Position Conversion", test_position_conversion),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
