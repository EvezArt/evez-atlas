"""Tests for quantum entanglement module"""

import pytest
from qiskit import QuantumCircuit

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from quantum_evez.entanglement import (
    BellState,
    BellStateType,
    EPRPair,
    EntanglementSimulator,
)


class TestBellState:
    """Test BellState dataclass"""
    
    def test_bell_state_creation(self):
        """Test creating a Bell state"""
        state = BellState(state_type=BellStateType.PHI_PLUS)
        assert state.state_type == BellStateType.PHI_PLUS
        assert state.fidelity == 1.0
        
    def test_bell_state_with_custom_fidelity(self):
        """Test Bell state with custom fidelity"""
        state = BellState(state_type=BellStateType.PSI_MINUS, fidelity=0.95)
        assert state.fidelity == 0.95
        
    def test_bell_state_invalid_fidelity(self):
        """Test that invalid fidelity raises error"""
        with pytest.raises(ValueError):
            BellState(state_type=BellStateType.PHI_PLUS, fidelity=1.5)
        
        with pytest.raises(ValueError):
            BellState(state_type=BellStateType.PHI_PLUS, fidelity=-0.1)


class TestEPRPair:
    """Test EPRPair dataclass"""
    
    def test_epr_pair_creation(self):
        """Test creating an EPR pair"""
        bell = BellState(state_type=BellStateType.PHI_PLUS)
        pair = EPRPair(qubit_a=0, qubit_b=1, bell_state=bell)
        assert pair.qubit_a == 0
        assert pair.qubit_b == 1
        assert pair.distance == 0.0
        
    def test_epr_pair_is_maximally_entangled(self):
        """Test maximal entanglement check"""
        bell_high = BellState(state_type=BellStateType.PHI_PLUS, fidelity=0.98)
        pair_high = EPRPair(qubit_a=0, qubit_b=1, bell_state=bell_high)
        assert pair_high.is_maximally_entangled()
        
        bell_low = BellState(state_type=BellStateType.PHI_PLUS, fidelity=0.85)
        pair_low = EPRPair(qubit_a=0, qubit_b=1, bell_state=bell_low)
        assert not pair_low.is_maximally_entangled()


class TestEntanglementSimulator:
    """Test EntanglementSimulator"""
    
    def test_simulator_initialization(self):
        """Test simulator can be initialized"""
        sim = EntanglementSimulator(shots=1000)
        assert sim.shots == 1000
        assert sim.backend is not None
        
    def test_create_bell_state_phi_plus(self):
        """Test creating Φ+ Bell state"""
        sim = EntanglementSimulator()
        circuit, bell_state = sim.create_bell_state(BellStateType.PHI_PLUS)
        
        assert isinstance(circuit, QuantumCircuit)
        assert circuit.num_qubits == 2
        assert bell_state.state_type == BellStateType.PHI_PLUS
        
    def test_create_bell_state_psi_minus(self):
        """Test creating Ψ- Bell state"""
        sim = EntanglementSimulator()
        circuit, bell_state = sim.create_bell_state(BellStateType.PSI_MINUS)
        
        assert isinstance(circuit, QuantumCircuit)
        assert bell_state.state_type == BellStateType.PSI_MINUS
        
    def test_create_epr_pair(self):
        """Test creating an EPR pair"""
        sim = EntanglementSimulator()
        epr_pair = sim.create_epr_pair((0, 1), BellStateType.PHI_PLUS)
        
        assert epr_pair.qubit_a == 0
        assert epr_pair.qubit_b == 1
        assert epr_pair.bell_state.state_type == BellStateType.PHI_PLUS
        assert epr_pair.distance == 1.0
        
    def test_measure_entanglement_fidelity(self):
        """Test measuring entanglement fidelity"""
        sim = EntanglementSimulator(shots=1000)
        circuit, _ = sim.create_bell_state(BellStateType.PHI_PLUS)
        
        fidelity = sim.measure_entanglement_fidelity(circuit)
        
        # For a perfect Bell state, fidelity should be close to 1.0
        assert 0.9 <= fidelity <= 1.0
        
    def test_simulate_noisy_channel(self):
        """Test adding noise to a circuit"""
        sim = EntanglementSimulator()
        circuit, _ = sim.create_bell_state(BellStateType.PHI_PLUS)
        
        noisy = sim.simulate_noisy_channel(circuit, depolarizing_prob=0.1)
        
        assert isinstance(noisy, QuantumCircuit)
        assert noisy.num_qubits == circuit.num_qubits
        
    def test_create_ghz_state(self):
        """Test creating a GHZ state"""
        sim = EntanglementSimulator()
        ghz = sim.create_ghz_state(num_qubits=3)
        
        assert isinstance(ghz, QuantumCircuit)
        assert ghz.num_qubits == 3
        
    def test_create_ghz_state_5_qubits(self):
        """Test creating a larger GHZ state"""
        sim = EntanglementSimulator()
        ghz = sim.create_ghz_state(num_qubits=5)
        
        assert ghz.num_qubits == 5
