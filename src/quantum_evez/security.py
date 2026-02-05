"""
Quantum Security Module

Implements security features including post-quantum cryptography concepts,
anomaly detection, and threat projection for quantum simulations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import hashlib
import secrets

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister


class ThreatLevel(Enum):
    """Severity levels for detected threats"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Represents a security event or anomaly"""
    timestamp: float
    event_type: str
    threat_level: ThreatLevel
    description: str
    metadata: Dict


class QuantumSecurity:
    """
    Post-quantum cryptography concepts and quantum-safe operations
    
    Note: This is a demonstration framework. For production use,
    rely on established cryptographic libraries like liboqs.
    """
    
    def __init__(self, security_parameter: int = 128):
        """
        Initialize quantum security module
        
        Args:
            security_parameter: Security level in bits (e.g., 128, 192, 256)
        """
        self.security_parameter = security_parameter
        
    def generate_quantum_random_key(self, key_length: int = 256) -> bytes:
        """
        Generate a cryptographically secure random key
        
        Args:
            key_length: Length of key in bits
            
        Returns:
            Random key as bytes
        """
        return secrets.token_bytes(key_length // 8)
    
    def quantum_key_distribution_bb84(
        self, 
        num_bits: int = 100
    ) -> Tuple[List[int], List[int], List[int]]:
        """
        Simulate BB84 quantum key distribution protocol
        
        Args:
            num_bits: Number of bits to exchange
            
        Returns:
            Tuple of (alice_bits, alice_bases, bob_bases)
        """
        # Alice generates random bits and bases
        alice_bits = [secrets.randbelow(2) for _ in range(num_bits)]
        alice_bases = [secrets.randbelow(2) for _ in range(num_bits)]
        
        # Bob chooses random measurement bases
        bob_bases = [secrets.randbelow(2) for _ in range(num_bits)]
        
        return alice_bits, alice_bases, bob_bases
    
    def create_bb84_circuit(
        self, 
        bit: int, 
        basis: int
    ) -> QuantumCircuit:
        """
        Create a single qubit BB84 state
        
        Args:
            bit: Bit value (0 or 1)
            basis: Encoding basis (0 for computational, 1 for Hadamard)
            
        Returns:
            Quantum circuit encoding the bit
        """
        qc = QuantumCircuit(1, 1)
        
        # Encode bit
        if bit == 1:
            qc.x(0)
            
        # Apply basis transformation
        if basis == 1:  # Hadamard basis
            qc.h(0)
            
        return qc
    
    def hash_quantum_state(self, circuit: QuantumCircuit) -> str:
        """
        Create a hash of a quantum circuit for integrity verification
        
        Args:
            circuit: Circuit to hash
            
        Returns:
            Hex digest of circuit hash
        """
        # Create a deterministic representation of the circuit
        # In Qiskit 1.0+, use qasm3 export instead of deprecated qasm()
        from qiskit import qasm2
        circuit_qasm = qasm2.dumps(circuit)
        
        # Hash using SHA-256
        hasher = hashlib.sha256()
        hasher.update(circuit_qasm.encode('utf-8'))
        
        return hasher.hexdigest()
    
    def verify_circuit_integrity(
        self, 
        circuit: QuantumCircuit, 
        expected_hash: str
    ) -> bool:
        """
        Verify that a circuit hasn't been tampered with
        
        Args:
            circuit: Circuit to verify
            expected_hash: Expected hash value
            
        Returns:
            True if circuit is authentic
        """
        current_hash = self.hash_quantum_state(circuit)
        return current_hash == expected_hash


class AnomalyDetector:
    """
    Detects anomalies in quantum simulations that might indicate
    security threats or system compromise
    """
    
    def __init__(self, baseline_threshold: float = 0.1):
        """
        Initialize anomaly detector
        
        Args:
            baseline_threshold: Threshold for anomaly detection
        """
        self.baseline_threshold = baseline_threshold
        self.baseline_metrics: Dict[str, float] = {}
        self.detected_events: List[SecurityEvent] = []
        
    def establish_baseline(
        self, 
        circuits: List[QuantumCircuit],
        metric_name: str = "fidelity"
    ) -> None:
        """
        Establish baseline metrics for normal operation
        
        Args:
            circuits: List of circuits to analyze
            metric_name: Name of metric to baseline
        """
        # Calculate baseline statistics
        # In a real implementation, this would be more sophisticated
        self.baseline_metrics[metric_name] = 0.95  # Placeholder
        
    def detect_fidelity_anomaly(
        self, 
        measured_fidelity: float,
        expected_fidelity: float = 0.95
    ) -> Optional[SecurityEvent]:
        """
        Detect if fidelity deviates suspiciously from expected
        
        Args:
            measured_fidelity: Observed fidelity
            expected_fidelity: Expected fidelity value
            
        Returns:
            SecurityEvent if anomaly detected, None otherwise
        """
        deviation = abs(measured_fidelity - expected_fidelity)
        
        if deviation > self.baseline_threshold:
            # Determine threat level
            if deviation > 0.3:
                threat_level = ThreatLevel.CRITICAL
            elif deviation > 0.2:
                threat_level = ThreatLevel.HIGH
            elif deviation > 0.15:
                threat_level = ThreatLevel.MEDIUM
            else:
                threat_level = ThreatLevel.LOW
                
            event = SecurityEvent(
                timestamp=0.0,  # Would use actual timestamp
                event_type="fidelity_anomaly",
                threat_level=threat_level,
                description=f"Fidelity deviation detected: {deviation:.3f}",
                metadata={
                    "measured": measured_fidelity,
                    "expected": expected_fidelity,
                    "deviation": deviation
                }
            )
            
            self.detected_events.append(event)
            return event
            
        return None
    
    def detect_gate_count_anomaly(
        self, 
        circuit: QuantumCircuit,
        expected_gate_count: Optional[int] = None
    ) -> Optional[SecurityEvent]:
        """
        Detect if circuit has suspicious number of gates
        
        Args:
            circuit: Circuit to analyze
            expected_gate_count: Expected number of gates
            
        Returns:
            SecurityEvent if anomaly detected
        """
        actual_gate_count = len(circuit.data)
        
        if expected_gate_count and abs(actual_gate_count - expected_gate_count) > 10:
            event = SecurityEvent(
                timestamp=0.0,
                event_type="gate_count_anomaly",
                threat_level=ThreatLevel.MEDIUM,
                description=f"Unexpected gate count: {actual_gate_count} (expected ~{expected_gate_count})",
                metadata={
                    "actual": actual_gate_count,
                    "expected": expected_gate_count
                }
            )
            
            self.detected_events.append(event)
            return event
            
        return None
    
    def detect_entanglement_anomaly(
        self,
        circuit: QuantumCircuit,
        max_entanglement_depth: int = 5
    ) -> Optional[SecurityEvent]:
        """
        Detect suspicious entanglement patterns that might indicate tampering
        
        Args:
            circuit: Circuit to analyze
            max_entanglement_depth: Maximum expected entanglement depth
            
        Returns:
            SecurityEvent if anomaly detected
        """
        # Count CNOT gates as a proxy for entanglement
        cnot_count = sum(1 for inst in circuit.data if inst.operation.name == 'cx')
        
        if cnot_count > max_entanglement_depth * circuit.num_qubits:
            event = SecurityEvent(
                timestamp=0.0,
                event_type="entanglement_anomaly",
                threat_level=ThreatLevel.HIGH,
                description=f"Excessive entanglement detected: {cnot_count} CNOT gates",
                metadata={
                    "cnot_count": cnot_count,
                    "num_qubits": circuit.num_qubits
                }
            )
            
            self.detected_events.append(event)
            return event
            
        return None
    
    def scan_circuit(self, circuit: QuantumCircuit) -> List[SecurityEvent]:
        """
        Comprehensive security scan of a quantum circuit
        
        Args:
            circuit: Circuit to scan
            
        Returns:
            List of detected security events
        """
        events = []
        
        # Check gate count
        gate_event = self.detect_gate_count_anomaly(circuit)
        if gate_event:
            events.append(gate_event)
            
        # Check entanglement
        ent_event = self.detect_entanglement_anomaly(circuit)
        if ent_event:
            events.append(ent_event)
            
        return events
    
    def get_threat_report(self) -> Dict[str, any]:
        """
        Generate a comprehensive threat report
        
        Returns:
            Dictionary containing threat statistics
        """
        total_events = len(self.detected_events)
        
        threat_counts = {
            ThreatLevel.LOW: 0,
            ThreatLevel.MEDIUM: 0,
            ThreatLevel.HIGH: 0,
            ThreatLevel.CRITICAL: 0
        }
        
        for event in self.detected_events:
            threat_counts[event.threat_level] += 1
            
        return {
            "total_events": total_events,
            "threat_breakdown": {
                level.value: count 
                for level, count in threat_counts.items()
            },
            "recent_events": [
                {
                    "type": event.event_type,
                    "level": event.threat_level.value,
                    "description": event.description
                }
                for event in self.detected_events[-10:]  # Last 10 events
            ]
        }
