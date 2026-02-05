#!/usr/bin/env python3
"""
QuantumEVEZ Demo Script

Demonstrates the key features of the quantum computing framework.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from quantum_evez import (
    EntanglementSimulator, 
    BellStateType,
    ShorCode,
    FidelityChecker,
    QuantumSecurity,
    AnomalyDetector
)
from qiskit import QuantumCircuit

def demo_entanglement():
    """Demonstrate entanglement physics"""
    print("\n" + "="*60)
    print("DEMO 1: Quantum Entanglement")
    print("="*60)
    
    sim = EntanglementSimulator(shots=1000)
    
    # Create Bell state
    print("\n1. Creating Bell State (Φ+)...")
    circuit, bell_state = sim.create_bell_state(BellStateType.PHI_PLUS)
    print(f"   State type: {bell_state.state_type.value}")
    print(f"   Initial fidelity: {bell_state.fidelity}")
    
    # Measure fidelity
    print("\n2. Measuring entanglement fidelity...")
    fidelity = sim.measure_entanglement_fidelity(circuit)
    print(f"   Measured fidelity: {fidelity:.4f}")
    print(f"   Status: {'✓ High quality' if fidelity > 0.95 else '✗ Needs improvement'}")
    
    # Create EPR pair
    print("\n3. Creating EPR pair...")
    epr_pair = sim.create_epr_pair((0, 1), BellStateType.PHI_PLUS)
    print(f"   Qubit A: {epr_pair.qubit_a}")
    print(f"   Qubit B: {epr_pair.qubit_b}")
    print(f"   Maximally entangled: {epr_pair.is_maximally_entangled()}")
    
    # Create GHZ state
    print("\n4. Creating GHZ state (3-qubit entanglement)...")
    ghz = sim.create_ghz_state(num_qubits=3)
    print(f"   Number of qubits: {ghz.num_qubits}")
    print("   Circuit:")
    print(ghz)

def demo_error_correction():
    """Demonstrate quantum error correction"""
    print("\n" + "="*60)
    print("DEMO 2: Quantum Error Correction")
    print("="*60)
    
    # Create a simple circuit
    print("\n1. Creating quantum circuit...")
    qc = QuantumCircuit(1)
    qc.h(0)
    print("   Circuit: H gate on qubit 0")
    
    # Use Shor code
    print("\n2. Applying Shor's 9-qubit error correction...")
    shor = ShorCode()
    encoded = shor.encode(qc)
    print(f"   Encoded qubits: {encoded.num_qubits}")
    print(f"   Protection: Bit-flip + Phase-flip")
    
    # Fidelity checking
    print("\n3. Self-healing with fidelity checker...")
    checker = FidelityChecker(target_fidelity=0.95)
    healed, success = checker.self_healing_cycle(qc, shor, max_iterations=2)
    print(f"   Self-healing successful: {success}")
    print(f"   Target fidelity: {checker.target_fidelity}")

def demo_security():
    """Demonstrate security features"""
    print("\n" + "="*60)
    print("DEMO 3: Quantum Security")
    print("="*60)
    
    qs = QuantumSecurity()
    
    # Generate quantum random key
    print("\n1. Generating quantum random key...")
    key = qs.generate_quantum_random_key(key_length=256)
    print(f"   Key length: {len(key)} bytes")
    print(f"   Key (first 16 bytes): {key[:16].hex()}")
    
    # BB84 quantum key distribution
    print("\n2. Simulating BB84 quantum key distribution...")
    alice_bits, alice_bases, bob_bases = qs.quantum_key_distribution_bb84(num_bits=50)
    matching_bases = sum(1 for a, b in zip(alice_bases, bob_bases) if a == b)
    print(f"   Total bits exchanged: {len(alice_bits)}")
    print(f"   Matching bases: {matching_bases}")
    print(f"   Key rate: {matching_bases/len(alice_bits)*100:.1f}%")
    
    # Circuit integrity
    print("\n3. Verifying circuit integrity...")
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    
    hash_value = qs.hash_quantum_state(qc)
    is_valid = qs.verify_circuit_integrity(qc, hash_value)
    print(f"   Circuit hash: {hash_value[:32]}...")
    print(f"   Integrity verified: {is_valid}")

def demo_anomaly_detection():
    """Demonstrate anomaly detection"""
    print("\n" + "="*60)
    print("DEMO 4: Anomaly Detection")
    print("="*60)
    
    detector = AnomalyDetector(baseline_threshold=0.1)
    
    # Test fidelity anomaly
    print("\n1. Testing fidelity anomaly detection...")
    event1 = detector.detect_fidelity_anomaly(0.95, 0.95)
    print(f"   Normal fidelity (0.95): {event1 is None and 'No anomaly' or 'Anomaly detected!'}")
    
    event2 = detector.detect_fidelity_anomaly(0.5, 0.95)
    if event2:
        print(f"   Low fidelity (0.5): Anomaly detected!")
        print(f"   Threat level: {event2.threat_level.value}")
    
    # Scan circuit
    print("\n2. Scanning quantum circuit for anomalies...")
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    
    events = detector.scan_circuit(qc)
    print(f"   Circuit gates: {len(qc.data)}")
    print(f"   Anomalies detected: {len(events)}")
    
    # Threat report
    print("\n3. Generating threat report...")
    report = detector.get_threat_report()
    print(f"   Total events: {report['total_events']}")
    print(f"   Critical threats: {report['threat_breakdown']['critical']}")
    print(f"   High threats: {report['threat_breakdown']['high']}")

def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("QuantumEVEZ - Quantum Computing Framework Demo")
    print("="*60)
    
    demo_entanglement()
    demo_error_correction()
    demo_security()
    demo_anomaly_detection()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nFor more information, see:")
    print("  - README.md")
    print("  - src/quantum_evez/ modules")
    print("  - src/tests/quantum/ test suite")
    print()

if __name__ == "__main__":
    main()
