"""Tests for quantum security module"""

import pytest
from qiskit import QuantumCircuit

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from quantum_evez.security import (
    ThreatLevel,
    SecurityEvent,
    QuantumSecurity,
    AnomalyDetector,
)


class TestQuantumSecurity:
    """Test QuantumSecurity module"""
    
    def test_quantum_security_initialization(self):
        """Test quantum security initialization"""
        qs = QuantumSecurity(security_parameter=128)
        assert qs.security_parameter == 128
        
    def test_generate_quantum_random_key(self):
        """Test quantum random key generation"""
        qs = QuantumSecurity()
        key = qs.generate_quantum_random_key(key_length=256)
        
        assert isinstance(key, bytes)
        assert len(key) == 32  # 256 bits = 32 bytes
        
    def test_generate_different_keys(self):
        """Test that generated keys are different"""
        qs = QuantumSecurity()
        key1 = qs.generate_quantum_random_key(key_length=128)
        key2 = qs.generate_quantum_random_key(key_length=128)
        
        assert key1 != key2
        
    def test_quantum_key_distribution_bb84(self):
        """Test BB84 protocol simulation"""
        qs = QuantumSecurity()
        alice_bits, alice_bases, bob_bases = qs.quantum_key_distribution_bb84(num_bits=50)
        
        assert len(alice_bits) == 50
        assert len(alice_bases) == 50
        assert len(bob_bases) == 50
        assert all(bit in [0, 1] for bit in alice_bits)
        
    def test_create_bb84_circuit_computational_basis(self):
        """Test creating BB84 circuit in computational basis"""
        qs = QuantumSecurity()
        circuit = qs.create_bb84_circuit(bit=0, basis=0)
        
        assert isinstance(circuit, QuantumCircuit)
        assert circuit.num_qubits == 1
        
    def test_create_bb84_circuit_hadamard_basis(self):
        """Test creating BB84 circuit in Hadamard basis"""
        qs = QuantumSecurity()
        circuit = qs.create_bb84_circuit(bit=1, basis=1)
        
        assert isinstance(circuit, QuantumCircuit)
        assert circuit.num_qubits == 1
        
    def test_hash_quantum_state(self):
        """Test hashing a quantum circuit"""
        qs = QuantumSecurity()
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        
        hash_value = qs.hash_quantum_state(qc)
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA-256 produces 64 hex characters
        
    def test_hash_is_deterministic(self):
        """Test that hashing is deterministic"""
        qs = QuantumSecurity()
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        
        hash1 = qs.hash_quantum_state(qc)
        hash2 = qs.hash_quantum_state(qc)
        
        assert hash1 == hash2
        
    def test_verify_circuit_integrity_valid(self):
        """Test verifying circuit integrity with correct hash"""
        qs = QuantumSecurity()
        qc = QuantumCircuit(2)
        qc.h(0)
        
        expected_hash = qs.hash_quantum_state(qc)
        is_valid = qs.verify_circuit_integrity(qc, expected_hash)
        
        assert is_valid is True
        
    def test_verify_circuit_integrity_invalid(self):
        """Test verifying circuit integrity with incorrect hash"""
        qs = QuantumSecurity()
        qc = QuantumCircuit(2)
        qc.h(0)
        
        fake_hash = "0" * 64
        is_valid = qs.verify_circuit_integrity(qc, fake_hash)
        
        assert is_valid is False


class TestAnomalyDetector:
    """Test AnomalyDetector module"""
    
    def test_anomaly_detector_initialization(self):
        """Test anomaly detector initialization"""
        detector = AnomalyDetector(baseline_threshold=0.1)
        assert detector.baseline_threshold == 0.1
        assert len(detector.detected_events) == 0
        
    def test_establish_baseline(self):
        """Test establishing baseline metrics"""
        detector = AnomalyDetector()
        circuits = [QuantumCircuit(2) for _ in range(5)]
        
        detector.establish_baseline(circuits, metric_name="fidelity")
        
        assert "fidelity" in detector.baseline_metrics
        
    def test_detect_fidelity_anomaly_no_deviation(self):
        """Test fidelity anomaly detection with no deviation"""
        detector = AnomalyDetector(baseline_threshold=0.1)
        
        event = detector.detect_fidelity_anomaly(
            measured_fidelity=0.95,
            expected_fidelity=0.95
        )
        
        assert event is None
        
    def test_detect_fidelity_anomaly_small_deviation(self):
        """Test fidelity anomaly detection with small deviation"""
        detector = AnomalyDetector(baseline_threshold=0.1)
        
        event = detector.detect_fidelity_anomaly(
            measured_fidelity=0.85,
            expected_fidelity=0.95
        )
        
        assert event is None  # Below threshold
        
    def test_detect_fidelity_anomaly_large_deviation(self):
        """Test fidelity anomaly detection with large deviation"""
        detector = AnomalyDetector(baseline_threshold=0.1)
        
        event = detector.detect_fidelity_anomaly(
            measured_fidelity=0.6,
            expected_fidelity=0.95
        )
        
        assert event is not None
        assert isinstance(event, SecurityEvent)
        assert event.threat_level == ThreatLevel.CRITICAL
        
    def test_detect_gate_count_anomaly(self):
        """Test gate count anomaly detection"""
        detector = AnomalyDetector()
        qc = QuantumCircuit(2)
        for _ in range(20):
            qc.h(0)
            qc.cx(0, 1)
        
        event = detector.detect_gate_count_anomaly(qc, expected_gate_count=5)
        
        assert event is not None
        assert event.event_type == "gate_count_anomaly"
        
    def test_detect_entanglement_anomaly_normal(self):
        """Test entanglement anomaly detection with normal circuit"""
        detector = AnomalyDetector()
        qc = QuantumCircuit(3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(0, 2)
        
        event = detector.detect_entanglement_anomaly(qc, max_entanglement_depth=5)
        
        assert event is None
        
    def test_detect_entanglement_anomaly_excessive(self):
        """Test entanglement anomaly detection with excessive entanglement"""
        detector = AnomalyDetector()
        qc = QuantumCircuit(3)
        # Add many CNOT gates
        for _ in range(20):
            qc.cx(0, 1)
            qc.cx(1, 2)
        
        event = detector.detect_entanglement_anomaly(qc, max_entanglement_depth=2)
        
        assert event is not None
        assert event.event_type == "entanglement_anomaly"
        assert event.threat_level == ThreatLevel.HIGH
        
    def test_scan_circuit(self):
        """Test comprehensive circuit scan"""
        detector = AnomalyDetector()
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        
        events = detector.scan_circuit(qc)
        
        assert isinstance(events, list)
        
    def test_get_threat_report_empty(self):
        """Test threat report with no events"""
        detector = AnomalyDetector()
        report = detector.get_threat_report()
        
        assert report["total_events"] == 0
        assert report["threat_breakdown"]["low"] == 0
        
    def test_get_threat_report_with_events(self):
        """Test threat report with detected events"""
        detector = AnomalyDetector()
        
        # Generate some events
        detector.detect_fidelity_anomaly(0.5, 0.95)
        detector.detect_fidelity_anomaly(0.7, 0.95)
        
        report = detector.get_threat_report()
        
        assert report["total_events"] >= 2
        assert "threat_breakdown" in report
        assert "recent_events" in report
