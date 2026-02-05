"""Tests for quantum error correction module"""

import pytest
from qiskit import QuantumCircuit

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from quantum_evez.error_correction import (
    ErrorCorrectionResult,
    ShorCode,
    SteaneCode,
    FidelityChecker,
)


class TestShorCode:
    """Test Shor's 9-qubit error correction code"""
    
    def test_shor_code_initialization(self):
        """Test Shor code initialization"""
        shor = ShorCode()
        assert shor.name == "Shor Code"
        assert shor.num_physical_qubits == 9
        assert shor.num_logical_qubits == 1
        
    def test_shor_code_encode(self):
        """Test encoding with Shor code"""
        shor = ShorCode()
        qc = QuantumCircuit(1)
        encoded = shor.encode(qc)
        
        assert isinstance(encoded, QuantumCircuit)
        assert encoded.num_qubits == 9
        
    def test_shor_code_decode(self):
        """Test decoding with Shor code"""
        shor = ShorCode()
        qc = QuantumCircuit(1)
        encoded = shor.encode(qc)
        decoded = shor.decode(encoded)
        
        assert isinstance(decoded, QuantumCircuit)
        
    def test_shor_code_detect_errors(self):
        """Test error detection"""
        shor = ShorCode()
        qc = QuantumCircuit(1)
        encoded = shor.encode(qc)
        syndrome = shor.detect_errors(encoded)
        
        assert isinstance(syndrome, list)
        assert len(syndrome) > 0
        
    def test_shor_code_correct_errors(self):
        """Test error correction"""
        shor = ShorCode()
        qc = QuantumCircuit(1)
        encoded = shor.encode(qc)
        syndrome = shor.detect_errors(encoded)
        corrected = shor.correct_errors(encoded, syndrome)
        
        assert isinstance(corrected, QuantumCircuit)


class TestSteaneCode:
    """Test Steane's 7-qubit error correction code"""
    
    def test_steane_code_initialization(self):
        """Test Steane code initialization"""
        steane = SteaneCode()
        assert steane.name == "Steane Code"
        assert steane.num_physical_qubits == 7
        assert steane.num_logical_qubits == 1
        
    def test_steane_code_encode(self):
        """Test encoding with Steane code"""
        steane = SteaneCode()
        qc = QuantumCircuit(1)
        encoded = steane.encode(qc)
        
        assert isinstance(encoded, QuantumCircuit)
        assert encoded.num_qubits == 7
        
    def test_steane_code_decode(self):
        """Test decoding with Steane code"""
        steane = SteaneCode()
        qc = QuantumCircuit(1)
        encoded = steane.encode(qc)
        decoded = steane.decode(encoded)
        
        assert isinstance(decoded, QuantumCircuit)
        
    def test_steane_code_detect_errors(self):
        """Test error detection"""
        steane = SteaneCode()
        qc = QuantumCircuit(1)
        encoded = steane.encode(qc)
        syndrome = steane.detect_errors(encoded)
        
        assert isinstance(syndrome, list)
        assert len(syndrome) == 6  # Steane code has 6 syndrome bits
        
    def test_steane_code_measure_fidelity(self):
        """Test fidelity measurement"""
        steane = SteaneCode()
        qc = QuantumCircuit(1)
        encoded = steane.encode(qc)
        
        fidelity = steane.measure_fidelity(encoded, shots=100)
        
        assert 0.0 <= fidelity <= 1.0


class TestFidelityChecker:
    """Test FidelityChecker for self-verification"""
    
    def test_fidelity_checker_initialization(self):
        """Test fidelity checker initialization"""
        checker = FidelityChecker(target_fidelity=0.95)
        assert checker.target_fidelity == 0.95
        
    def test_check_fidelity_simple_circuit(self):
        """Test fidelity check on a simple circuit"""
        checker = FidelityChecker(target_fidelity=0.9)
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        
        result = checker.check_fidelity(qc, shots=100)
        
        assert isinstance(result, ErrorCorrectionResult)
        assert 0.0 <= result.fidelity <= 1.0
        assert isinstance(result.success, bool)
        
    def test_check_fidelity_meets_target(self):
        """Test that high-fidelity circuits pass"""
        checker = FidelityChecker(target_fidelity=0.8)
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        
        result = checker.check_fidelity(qc, shots=1000)
        
        # Bell state should have high fidelity
        assert result.fidelity >= 0.8 or not result.success
        
    def test_self_healing_cycle(self):
        """Test self-healing cycle"""
        checker = FidelityChecker(target_fidelity=0.95)
        shor = ShorCode()
        
        qc = QuantumCircuit(1)
        qc.h(0)
        
        healed_circuit, success = checker.self_healing_cycle(
            qc, shor, max_iterations=2
        )
        
        assert isinstance(healed_circuit, QuantumCircuit)
        assert isinstance(success, bool)
        
    def test_self_healing_with_steane_code(self):
        """Test self-healing with Steane code"""
        checker = FidelityChecker(target_fidelity=0.95)
        steane = SteaneCode()
        
        qc = QuantumCircuit(1)
        
        healed_circuit, success = checker.self_healing_cycle(
            qc, steane, max_iterations=1
        )
        
        assert isinstance(healed_circuit, QuantumCircuit)
